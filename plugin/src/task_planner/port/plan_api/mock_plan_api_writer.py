"""계획 저장소 쓰기의 mock 구현. .mockData/ 의 파일에 쓴다.
메서드마다 계획 파일 하나를 읽고, 바꾼 계획을 통째로 다시 저장한다."""

from __future__ import annotations

from dataclasses import replace

from task_planner.common.clock import utc_now
from task_planner.common.mock_data import next_mock_id
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.mock_plan_files import load_plan, save_plan
from task_planner.port.plan_api.plan_api_error import PlanApiError
from task_planner.port.plan_api.plan_api_writer import PlanApiWriter


class MockPlanApiWriter(PlanApiWriter):
    def create_plan(self, new_plan: NewPlan) -> Plan:
        # 새 id 를 받아 노드·간선이 없는 작성 중 계획을 만들어 저장한다
        plan = Plan(
            plan_id=next_mock_id("plan"),
            title=new_plan.title,
            request=new_plan.request,
            persona_ids=new_plan.persona_ids,
            status=PlanStatus.DRAFTING,
            created_at=utc_now(),
            nodes=(),
            edges=(),
        )
        save_plan(plan)
        return plan

    def add_node(self, plan_id: int, new_node: NewNode) -> PlanNode:
        # 새 id 와 todo 상태로 노드를 만들어 계획 끝에 붙인다.
        # POST 라 같은 요청을 두 번 보내면 노드가 둘 생긴다. 서버도 같다고 보고 막지 않는다
        plan = load_plan(plan_id)
        node = PlanNode(
            node_id=next_mock_id("node"),
            title=new_node.title,
            kind=new_node.kind,
            persona_ids=new_node.persona_ids,
            output_spec=new_node.output_spec,
            status=PlanNodeStatus.TODO,
        )
        save_plan(replace(plan, nodes=(*plan.nodes, node)))
        return node

    def add_edge(self, plan_id: int, from_node_id: int, to_node_id: int) -> PlanEdge:
        # 양 끝 노드가 있는지 보고, 같은 간선이 이미 있으면 그것을, 없으면 새로 만들어 돌려준다
        plan = load_plan(plan_id)
        _require_nodes_exist(plan, from_node_id, to_node_id)
        existing_edge = _find_edge(plan, from_node_id, to_node_id)
        if existing_edge is not None:
            return existing_edge
        edge = PlanEdge(edge_id=next_mock_id("edge"), from_node_id=from_node_id, to_node_id=to_node_id)
        save_plan(replace(plan, edges=(*plan.edges, edge)))
        return edge

    def update_node(self, plan_id: int, node_id: int, change: NodeChange) -> PlanNode:
        # 노드를 찾아 change 에서 값이 있는 필드만 바꾸고, 계획 안의 그 노드를 바꾼 노드로 갈아 끼운다
        plan = load_plan(plan_id)
        changed_node = _apply_change(_find_node(plan, node_id), change)
        save_plan(replace(plan, nodes=_replace_node(plan.nodes, changed_node)))
        return changed_node

    def delete_node(self, plan_id: int, node_id: int) -> None:
        # 노드와, 그 노드가 앞이나 뒤에 있는 간선을 함께 뺀다
        plan = load_plan(plan_id)
        remaining_nodes = tuple(node for node in plan.nodes if node.node_id != node_id)
        remaining_edges = tuple(edge for edge in plan.edges if node_id not in (edge.from_node_id, edge.to_node_id))
        save_plan(replace(plan, nodes=remaining_nodes, edges=remaining_edges))

    def delete_edge(self, plan_id: int, edge_id: int) -> None:
        # 그 id 의 간선만 뺀다
        plan = load_plan(plan_id)
        save_plan(replace(plan, edges=tuple(edge for edge in plan.edges if edge.edge_id != edge_id)))

    def set_plan_status(self, plan_id: int, status: PlanStatus) -> Plan:
        # 상태만 바꿔 저장한다. 허용하는 바꾸기인지는 부르는 쪽이 이미 봤다
        plan = replace(load_plan(plan_id), status=status)
        save_plan(plan)
        return plan


def _require_nodes_exist(plan: Plan, from_node_id: int, to_node_id: int) -> None:
    node_ids = {node.node_id for node in plan.nodes}
    if from_node_id not in node_ids or to_node_id not in node_ids:
        raise PlanApiError(f"계획 {plan.plan_id}: 간선 {from_node_id} → {to_node_id} 의 노드가 없습니다")


def _find_edge(plan: Plan, from_node_id: int, to_node_id: int) -> PlanEdge | None:
    for edge in plan.edges:
        if edge.from_node_id == from_node_id and edge.to_node_id == to_node_id:
            return edge
    return None


def _find_node(plan: Plan, node_id: int) -> PlanNode:
    try:
        return plan.node(node_id)
    except KeyError as missing:
        raise PlanApiError(f"계획 {plan.plan_id}: 고칠 노드 {node_id} 가 없습니다") from missing


def _apply_change(node: PlanNode, change: NodeChange) -> PlanNode:
    """change 에서 None 이 아닌 필드만 바꾼 새 노드."""
    return replace(
        node,
        title=node.title if change.title is None else change.title,
        kind=node.kind if change.kind is None else change.kind,
        persona_ids=node.persona_ids if change.persona_ids is None else change.persona_ids,
        output_spec=node.output_spec if change.output_spec is None else change.output_spec,
        status=node.status if change.status is None else change.status,
    )


def _replace_node(nodes: tuple[PlanNode, ...], changed_node: PlanNode) -> tuple[PlanNode, ...]:
    return tuple(changed_node if node.node_id == changed_node.node_id else node for node in nodes)
