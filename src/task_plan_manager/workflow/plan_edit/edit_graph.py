"""계획의 노드와 간선을 메모리에 복사해 묶음 동작을 적용한다. 정의서 만들기도 여기서 한다.
나누기·합치기·넣기·빼기는 노드만 바꾸고, 간선 다시 정하기에 넘길 것을 모은다.
모으는 것: 원래 노드, 바뀐 노드, 앞뒤 노드, 이전 간선.
간선은 간선 다시 정하기의 결과로 apply_relinked 가 바꾼다 (사용자, 2026-11-19: LLM 이 정의서를 보고 잇는다).
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
from task_plan_manager.workflow.plan_edit.op.unlink_op import UnlinkOp
from task_plan_manager.workflow.plan_edit.op.update_op import UpdateOp
from task_plan_manager.workflow.plan_edit.plan_edit_refused_error import PlanEditRefusedError
from task_plan_manager.workflow.relink_edges.relink_node import RelinkNode
from task_plan_manager.workflow.relink_edges.relink_request import RelinkRequest

Edge = tuple[int, int]  # (앞 노드 id, 뒤 노드 id)


class EditGraph:
    """계획의 노드와 간선을 메모리에 복사해 묶음 동작을 적용한다."""

    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        self.nodes: dict[int, PlanNode] = {node.node_id: node for node in plan.nodes}
        self.edges: set[Edge] = {(edge.from_node_id, edge.to_node_id) for edge in plan.edges}
        self._edge_ids = {(edge.from_node_id, edge.to_node_id): edge.edge_id for edge in plan.edges}  # 원래 간선 id
        # 사람이 읽는 바뀐 것. 새 노드는 임시 id 로 적었다가 send_edit 이 진짜 id 로 바꾼다
        self.changes: list[str] = []
        self._next_temporary_id = -1
        # 간선 다시 정하기에 넘길 것
        self._relink_changes: list[str] = []  # 바꾼 내용 (프롬프트의 change)
        self._originals: dict[int, PlanNode] = {}  # 지워진 원래 노드
        self._changed: list[int] = []  # 생긴 노드
        self._neighbors: set[int] = set()  # 원래 노드의 앞뒤 노드
        self._previous_edges: set[Edge] = set()  # 바뀌기 전, 원래 노드와 앞뒤 노드 사이의 간선
        self._user_links: list[Edge] = []
        self._user_unlinks: list[Edge] = []

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

    # --- 간선 다시 정하기 ---
    def relink_request(self) -> RelinkRequest | None:
        """나누기·합치기·넣기·빼기가 있었으면 간선 다시 정하기의 입력. 없거나, 다시 정할 노드가 없으면 None."""
        if not self._relink_changes:
            return None
        changed = [node_id for node_id in self._changed if node_id in self.nodes]
        neighbors = sorted(node_id for node_id in self._neighbors if node_id in self.nodes and node_id not in changed)
        if len(changed) + len(neighbors) < 2:  # 이을 수 있는 짝이 없다 (앞뒤 없이 빼거나 넣음)
            return None
        scope = set(changed) | set(neighbors)
        # 이전 간선: 동작마다 모은 것에 지금 범위 노드끼리의 간선을 더한다. 동작이 여럿이면 서로 다른 동작의 노드 사이도
        previous = self._previous_edges | {edge for edge in self.edges if edge[0] in scope and edge[1] in scope}
        outside = tuple(sorted(edge for edge in self.edges if not (edge[0] in scope and edge[1] in scope)))
        return RelinkRequest(
            change="\n".join(self._relink_changes),
            original_nodes=tuple(_relink_node(node) for node_id, node in self._originals.items()
                                 if node_id not in self.nodes),
            changed_nodes=tuple(_relink_node(self.nodes[node_id]) for node_id in changed),
            neighbor_nodes=tuple(_relink_node(self.nodes[node_id]) for node_id in neighbors),
            previous_edges=tuple(sorted(previous)),
            user_links=tuple(self._user_links),
            user_unlinks=tuple(self._user_unlinks),
            outside_edges=outside,
        )  # fmt: skip

    def apply_relinked(self, request: RelinkRequest, edges: Iterable[Edge]) -> None:
        """바뀐 노드와 앞뒤 노드 사이의 간선을 받은 간선으로 바꾼다. 그 밖의 노드와 이어진 간선은 그대로 둔다."""
        scope = request.scope_ids()
        self.edges = {edge for edge in self.edges if not (edge[0] in scope and edge[1] in scope)}
        self.edges.update(edges)

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
        """원래 노드를 새 노드들로 바꾼다. 종류는 새 노드마다 (없으면 원래 노드), 담당은 원래 노드를 따른다."""
        original = self._existing(op.node_id)
        self._note_neighbors([original])
        self._drop(op.node_id)
        new_ids = [self._add(part, part.kind or original.kind, original) for part in op.into]
        self._changed += new_ids
        self.changes.append(f"나눔: {_label(original)} → {self._labels(new_ids)}")
        self._relink_changes.append(f'{original.node_id} "{original.title}" 을 {_ids(new_ids)} 으로 나눔')

    def _merge(self, op: MergeOp) -> None:
        """노드 하나로 합친다. 담당은 합칠 노드들의 담당을 모두 모은다."""
        originals = [self._existing(node_id) for node_id in op.node_ids]
        self._note_neighbors(originals)
        persona_ids = tuple(_unique(persona_id for original in originals for persona_id in original.persona_ids))
        for node_id in op.node_ids:
            self._drop(node_id)
        merged = replace(originals[0], persona_ids=persona_ids)
        new_id = self._add(op.part, op.part.kind or originals[0].kind, merged)
        self._changed.append(new_id)
        self.changes.append(f"합침: {', '.join(_label(original) for original in originals)} → {self._label_of(new_id)}")
        self._relink_changes.append(f'{_ids(op.node_ids)} 을 {new_id} "{op.part.title}" 로 합침')

    def _insert(self, op: InsertOp) -> None:
        """새 노드를 더한다. after, before 는 앞뒤 노드로 넘긴다. 확인 노드면 담당을 비운다."""
        neighbors = [self._existing(node_id) for node_id in (op.after, op.before) if node_id is not None]
        assert op.part.kind is not None  # 읽을 때 검사했다
        new_id = self._add(op.part, op.part.kind, None)
        self._changed.append(new_id)
        ids = {node.node_id for node in neighbors}
        self._neighbors.update(ids)
        self._previous_edges.update(edge for edge in self.edges if edge[0] in ids and edge[1] in ids)
        self.changes.append(f"넣음: {self._label_of(new_id)}")
        self._relink_changes.append(f'{_where(op)}{new_id} "{op.part.title}" 를 넣음')

    def _remove(self, op: RemoveOp) -> None:
        """노드를 지운다. 앞 노드와 뒤 노드를 이을지는 간선 다시 정하기가 정한다."""
        original = self._existing(op.node_id)
        self._note_neighbors([original])
        self._drop(op.node_id)
        self.changes.append(f"뺌: {_label(original)}")
        self._relink_changes.append(f'{original.node_id} "{original.title}" 를 뺌')

    def _update(self, op: UpdateOp) -> None:
        original = self._existing(op.node_id)
        spec = change_spec(original.output_spec, op.does, op.output, op.add_note)
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
        """사용자가 이으라고 한 간선. 간선 다시 정하기도 이 간선을 남긴다."""
        self._existing(op.from_node_id), self._existing(op.to_node_id)
        self.edges.add((op.from_node_id, op.to_node_id))
        self._user_links.append((op.from_node_id, op.to_node_id))

    def _unlink(self, op: UnlinkOp) -> None:
        """사용자가 끊으라고 한 간선. 간선 다시 정하기도 이 간선을 다시 잇지 않는다."""
        if (op.from_node_id, op.to_node_id) not in self.edges:
            raise PlanEditRefusedError(f"간선 {op.from_node_id} → {op.to_node_id} 가 없습니다")
        self.edges.discard((op.from_node_id, op.to_node_id))
        self._user_unlinks.append((op.from_node_id, op.to_node_id))

    # --- 노드와 간선 다루기 ---
    def _existing(self, node_id: int) -> PlanNode:
        """지금(앞 동작을 적용한 뒤) 있는 노드. 없으면 거절."""
        if node_id not in self.nodes:
            raise PlanEditRefusedError(f"노드 {node_id} 가 계획에 없습니다")
        return self.nodes[node_id]

    def _note_neighbors(self, originals: list[PlanNode]) -> None:
        """지울 원래 노드와 그 앞뒤 노드, 그 사이의 간선을 간선 다시 정하기에 넘길 것으로 모은다."""
        original_ids = {original.node_id for original in originals}
        for original in originals:
            self._originals.setdefault(original.node_id, original)
        neighbors = {other for edge in self.edges if set(edge) & original_ids for other in edge} - original_ids
        self._neighbors.update(neighbors)
        known = original_ids | neighbors
        self._previous_edges.update(edge for edge in self.edges if edge[0] in known and edge[1] in known)

    def _add(self, part: NewPart, kind: NodeKind, base: PlanNode | None) -> int:
        """새 노드. 담당은 확인 노드면 없음, 아니면 base 의 담당 (없으면 계획의 첫 페르소나)."""
        node_id = self._next_temporary_id
        self._next_temporary_id -= 1
        persona_ids: tuple[int, ...] = ()
        if kind is not NodeKind.HITL:
            persona_ids = (base.persona_ids if base else ()) or self.plan.persona_ids[:1]
        self.nodes[node_id] = PlanNode(node_id, part.title, kind, persona_ids, new_spec(part), PlanNodeStatus.TODO)
        return node_id

    def _drop(self, node_id: int) -> None:
        """노드와 닿은 간선을 지운다."""
        del self.nodes[node_id]
        self.edges = {edge for edge in self.edges if node_id not in edge}

    def _label_of(self, node_id: int) -> str:
        return _label(self.nodes[node_id])

    def _labels(self, node_ids: list[int]) -> str:
        return ", ".join(self._label_of(node_id) for node_id in node_ids)


def _label(node: PlanNode) -> str:
    """바뀐 것 글에 쓰는 이름. 새 노드(음수 id)는 send_edit 이 진짜 id 로 바꾼다."""
    return f"{{{node.node_id}}} {node.title}"


def _relink_node(node: PlanNode) -> RelinkNode:
    return RelinkNode(node.node_id, node.title, node.kind.value, node.output_spec)


def _ids(node_ids: Iterable[int]) -> str:
    return ", ".join(str(node_id) for node_id in node_ids)


def _where(op: InsertOp) -> str:
    """넣은 자리. 예: "36 과 37 사이에 "."""
    if op.after is not None and op.before is not None:
        return f"{op.after} 과 {op.before} 사이에 "
    if op.after is not None:
        return f"{op.after} 뒤에 "
    if op.before is not None:
        return f"{op.before} 앞에 "
    return ""


def _unique(values: Iterable[int]) -> list[int]:
    """순서를 지키며 겹친 값을 뺀다."""
    return list(dict.fromkeys(values))
