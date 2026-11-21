"""고치기 전 계획과 EditGraph 를 비교해 계획 저장소에 보낸다.
순서: 노드 추가 → 노드 고치기 → 간선 지우기 → 간선 추가 → 노드 지우기. 중간에 실패하면 되돌리지 않는다."""

from __future__ import annotations

from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_node import PlanNode
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.plan_api_writer import PlanApiWriter
from task_planner.workflow.plan_edit.edit_graph import EditGraph


def send_edit(before: Plan, graph: EditGraph, writer: PlanApiWriter, sent: list[str]) -> dict[int, int]:
    """바뀐 것을 보내고 임시 id → 진짜 id 를 돌려준다. 보낸 요청은 sent 에 차례로 적는다 (실패해도 남는다)."""
    plan_id = before.plan_id
    real_ids = _add_nodes(plan_id, graph, writer, sent)
    _update_nodes(plan_id, before, graph, writer, sent)
    _delete_edges(plan_id, before, graph, writer, sent)
    _add_edges(plan_id, before, graph, real_ids, writer, sent)
    _delete_nodes(plan_id, before, graph, writer, sent)
    return real_ids


def _add_nodes(plan_id: int, graph: EditGraph, writer: PlanApiWriter, sent: list[str]) -> dict[int, int]:
    real_ids: dict[int, int] = {}
    for node in graph.nodes.values():
        if node.node_id < 0:
            saved = writer.add_node(plan_id, NewNode(node.title, node.kind, node.persona_ids, node.output_spec))
            real_ids[node.node_id] = saved.node_id
            sent.append(f"노드 추가 {saved.node_id} {saved.title}")
    return real_ids


def _update_nodes(plan_id: int, before: Plan, graph: EditGraph, writer: PlanApiWriter, sent: list[str]) -> None:
    for old in before.nodes:
        new = graph.nodes.get(old.node_id)
        if new is None:
            continue
        change = _node_change(old, new)
        if change != NodeChange():
            writer.update_node(plan_id, old.node_id, change)
            sent.append(f"노드 고치기 {old.node_id} {new.title}")


def _node_change(old: PlanNode, new: PlanNode) -> NodeChange:
    """다른 값만 담는다."""
    return NodeChange(
        title=new.title if new.title != old.title else None,
        kind=new.kind if new.kind != old.kind else None,
        persona_ids=new.persona_ids if new.persona_ids != old.persona_ids else None,
        output_spec=new.output_spec if new.output_spec != old.output_spec else None,
    )


def _delete_edges(plan_id: int, before: Plan, graph: EditGraph, writer: PlanApiWriter, sent: list[str]) -> None:
    for edge in before.edges:
        if (edge.from_node_id, edge.to_node_id) not in graph.edges:
            writer.delete_edge(plan_id, edge.edge_id)
            sent.append(f"간선 지우기 {edge.from_node_id} → {edge.to_node_id}")


def _add_edges(plan_id: int, before: Plan, graph: EditGraph, real_ids: dict[int, int], writer: PlanApiWriter,
               sent: list[str]) -> None:  # fmt: skip
    existing = {(edge.from_node_id, edge.to_node_id) for edge in before.edges}
    for from_id, to_id in sorted(graph.edges):
        if (from_id, to_id) in existing:
            continue
        from_real, to_real = real_ids.get(from_id, from_id), real_ids.get(to_id, to_id)
        writer.add_edge(plan_id, from_real, to_real)
        sent.append(f"간선 추가 {from_real} → {to_real}")


def _delete_nodes(plan_id: int, before: Plan, graph: EditGraph, writer: PlanApiWriter, sent: list[str]) -> None:
    for node in before.nodes:
        if node.node_id not in graph.nodes:
            writer.delete_node(plan_id, node.node_id)
            sent.append(f"노드 지우기 {node.node_id} {node.title}")
