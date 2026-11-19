"""계획의 노드와 간선을 메모리에 복사해 묶음 동작을 적용한다. 앞뒤 다시 잇기와 정의서 만들기도 여기서 한다.
새 노드는 음수 임시 id 를 받는다. 계획 저장소에 보내는 일은 send_edit 이 한다."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_edge import PlanEdge
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.workflow.plan_edit.node_spec import change_spec, new_spec
from task_plan_manager.workflow.plan_edit.op.edit_op import EditOp
from task_plan_manager.workflow.plan_edit.op.insert_op import InsertOp
from task_plan_manager.workflow.plan_edit.op.link_op import LinkOp
from task_plan_manager.workflow.plan_edit.op.merge_op import MergeOp
from task_plan_manager.workflow.plan_edit.op.new_part import NewPart
from task_plan_manager.workflow.plan_edit.op.remove_op import RemoveOp
from task_plan_manager.workflow.plan_edit.op.split_op import SplitOp
from task_plan_manager.workflow.plan_edit.op.split_order import SplitOrder
from task_plan_manager.workflow.plan_edit.op.unlink_op import UnlinkOp
from task_plan_manager.workflow.plan_edit.op.update_op import UpdateOp
from task_plan_manager.workflow.plan_edit.plan_edit_refused_error import PlanEditRefusedError

Edge = tuple[int, int]  # (앞 노드 id, 뒤 노드 id)


class EditGraph:
    """계획의 노드와 간선을 메모리에 복사해 묶음 동작을 적용한다."""

    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        self.nodes: dict[int, PlanNode] = {node.node_id: node for node in plan.nodes}
        self.edges: set[Edge] = {(edge.from_node_id, edge.to_node_id) for edge in plan.edges}
        self._edge_ids = {(edge.from_node_id, edge.to_node_id): edge.edge_id for edge in plan.edges}  # 원래 간선 id
        self.changes: list[
            str
        ] = []  # 사람이 읽는 바뀐 것. 새 노드는 임시 id 로 적었다가 send_edit 이 진짜 id 로 바꾼다
        self._next_temporary_id = -1

    def apply_all(self, ops: tuple[EditOp, ...]) -> None:
        for index, op in enumerate(ops, 1):
            try:
                self._apply(op)
            except PlanEditRefusedError as error:
                raise PlanEditRefusedError(f"{index} 번째 동작: {error}") from error

    def as_plan(self) -> Plan:
        """바뀐 모습의 Plan (문제 점검용). 원래 간선은 원래 id, 새 간선은 원래 id 뒤의 번호를 받는다."""
        next_id = max(self._edge_ids.values(), default=0)
        edges = []
        for from_id, to_id in sorted(self.edges):
            edge_id = self._edge_ids.get((from_id, to_id))
            if edge_id is None:
                next_id += 1
                edge_id = next_id
            edges.append(PlanEdge(edge_id, from_id, to_id))
        return replace(self.plan, nodes=tuple(self.nodes.values()), edges=tuple(edges))

    # --- 동작마다 ---
    def _apply(self, op: EditOp) -> None:
        if isinstance(op, SplitOp):
            self._split(op)
        elif isinstance(op, MergeOp):
            self._merge(op)
        elif isinstance(op, InsertOp):
            self._insert(op)
        elif isinstance(op, RemoveOp):
            self._remove(op)
        elif isinstance(op, UpdateOp):
            self._update(op)
        elif isinstance(op, LinkOp):
            self._link(op)
        else:
            self._unlink(op)

    def _split(self, op: SplitOp) -> None:
        """원래 노드를 새 노드들로 바꾼다. 종류와 담당은 원래 노드를 따른다."""
        original = self._existing(op.node_id)
        before_ids, after_ids = self._before(op.node_id), self._after(op.node_id)
        self._drop(op.node_id)
        new_ids = [self._add(part, original.kind, original.persona_ids) for part in op.into]
        if op.order is SplitOrder.SERIAL:
            self._connect(before_ids, new_ids[:1])
            for from_id, to_id in zip(new_ids, new_ids[1:], strict=False):
                self.edges.add((from_id, to_id))
            self._connect(new_ids[-1:], after_ids)
        else:
            self._connect(before_ids, new_ids)
            self._connect(new_ids, after_ids)
        new_labels = ", ".join(self._label_of(node_id) for node_id in new_ids)
        self.changes.append(f"나눔: {_label(original)} → {new_labels}")

    def _merge(self, op: MergeOp) -> None:
        """노드 하나로 합친다. 합칠 노드들의 앞·뒤 노드를 모두 잇고, 합쳐진 노드끼리의 간선은 없앤다."""
        originals = [self._existing(node_id) for node_id in op.node_ids]
        merged = set(op.node_ids)
        before_ids = _unique(node_id for original in originals for node_id in self._before(original.node_id))
        after_ids = _unique(node_id for original in originals for node_id in self._after(original.node_id))
        persona_ids = tuple(_unique(persona_id for original in originals for persona_id in original.persona_ids))
        for node_id in op.node_ids:
            self._drop(node_id)
        new_id = self._add(op.part, originals[0].kind, persona_ids)
        self._connect([node_id for node_id in before_ids if node_id not in merged], [new_id])
        self._connect([new_id], [node_id for node_id in after_ids if node_id not in merged])
        joined = ", ".join(_label(original) for original in originals)
        self.changes.append(f"합침: {joined} → {self._label_of(new_id)}")

    def _insert(self, op: InsertOp) -> None:
        """after → 새 노드 → before 로 잇고 after → before 간선은 지운다. 확인 노드면 담당을 비운다."""
        for node_id in (op.after, op.before):
            if node_id is not None:
                self._existing(node_id)
        persona_ids = () if op.kind is NodeKind.HITL else self.plan.persona_ids[:1]
        new_id = self._add(op.part, op.kind, persona_ids)
        if op.after is not None:
            self.edges.add((op.after, new_id))
        if op.before is not None:
            self.edges.add((new_id, op.before))
        if op.after is not None and op.before is not None:
            self.edges.discard((op.after, op.before))
        self.changes.append(f"넣음: {self._label_of(new_id)}")

    def _remove(self, op: RemoveOp) -> None:
        """노드를 지우고 앞 노드 각각 → 뒤 노드 각각을 바로 잇는다."""
        original = self._existing(op.node_id)
        before_ids, after_ids = self._before(op.node_id), self._after(op.node_id)
        self._drop(op.node_id)
        self._connect(before_ids, after_ids)
        self.changes.append(f"뺌: {_label(original)} (앞뒤를 바로 이음)")

    def _update(self, op: UpdateOp) -> None:
        original = self._existing(op.node_id)
        spec = change_spec(original.output_spec, op.scope, op.output, op.add_note)
        kind = op.kind or original.kind
        changed = replace(original, title=op.title or original.title, kind=kind,
                          persona_ids=self._updated_personas(original, kind, op.persona_ids),
                          output_spec=spec)  # fmt: skip
        self.nodes[op.node_id] = changed
        self.changes.append(f"고침: {_label(changed)}")

    def _updated_personas(self, original: PlanNode, kind: NodeKind, given: tuple[int, ...] | None) -> tuple[int, ...]:
        """확인 노드는 담당을 비운다. 확인 노드를 작업 노드로 바꾸면서 담당을 주지 않았으면 계획의 첫 페르소나."""
        if kind is NodeKind.HITL:
            return ()
        if given:
            return given
        if original.kind is NodeKind.HITL:
            return self.plan.persona_ids[:1]
        return original.persona_ids

    def _link(self, op: LinkOp) -> None:
        self._existing(op.from_node_id), self._existing(op.to_node_id)
        self.edges.add((op.from_node_id, op.to_node_id))
        self.changes.append(f"이음: {self._label_of(op.from_node_id)} → {self._label_of(op.to_node_id)}")

    def _unlink(self, op: UnlinkOp) -> None:
        if (op.from_node_id, op.to_node_id) not in self.edges:
            raise PlanEditRefusedError(f"간선 {op.from_node_id} → {op.to_node_id} 가 없습니다")
        self.edges.discard((op.from_node_id, op.to_node_id))
        self.changes.append(f"끊음: {self._label_of(op.from_node_id)} → {self._label_of(op.to_node_id)}")

    # --- 노드와 간선 다루기 ---
    def _existing(self, node_id: int) -> PlanNode:
        """지금(앞 동작을 적용한 뒤) 있는 노드. 없으면 거절."""
        if node_id not in self.nodes:
            raise PlanEditRefusedError(f"노드 {node_id} 가 계획에 없습니다")
        return self.nodes[node_id]

    def _add(self, part: NewPart, kind: NodeKind, persona_ids: tuple[int, ...]) -> int:
        node_id = self._next_temporary_id
        self._next_temporary_id -= 1
        spec = new_spec(part.scope, part.output, part.note)
        self.nodes[node_id] = PlanNode(node_id, part.title, kind, persona_ids, spec, PlanNodeStatus.TODO)
        return node_id

    def _drop(self, node_id: int) -> None:
        """노드와 닿은 간선을 지운다."""
        del self.nodes[node_id]
        self.edges = {edge for edge in self.edges if node_id not in edge}

    def _before(self, node_id: int) -> list[int]:
        return sorted(from_id for from_id, to_id in self.edges if to_id == node_id)

    def _after(self, node_id: int) -> list[int]:
        return sorted(to_id for from_id, to_id in self.edges if from_id == node_id)

    def _connect(self, from_ids: list[int], to_ids: list[int]) -> None:
        for from_id in from_ids:
            for to_id in to_ids:
                if from_id != to_id:
                    self.edges.add((from_id, to_id))

    def _label_of(self, node_id: int) -> str:
        return _label(self.nodes[node_id])


def _label(node: PlanNode) -> str:
    """바뀐 것 글에 쓰는 이름. 새 노드(음수 id)는 send_edit 이 진짜 id 로 바꾼다."""
    return f"{{{node.node_id}}} {node.title}"


def _unique(values: Iterable[int]) -> list[int]:
    """순서를 지키며 겹친 값을 뺀다."""
    return list(dict.fromkeys(values))
