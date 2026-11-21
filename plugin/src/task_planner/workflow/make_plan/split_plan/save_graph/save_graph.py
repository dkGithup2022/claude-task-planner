"""split_plan 의 마지막 기능. 저장 전 노드와 간선을 계획 저장소에 저장한다.
노드를 먼저 저장해 서버 id 를 받고, 그 id 로 간선을 바꿔 저장한다.
split_plan 을 다시 수행하면 앞선 시도가 남긴 노드를 지우고 새로 저장한다.
지우는 것은 작성 중인 계획에서만 한다 (사용자, 2026-11-19)."""

from __future__ import annotations

from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.plan_api_reader import PlanApiReader
from task_planner.port.plan_api.plan_api_writer import PlanApiWriter
from task_planner.workflow.make_plan.split_plan.save_graph.plan_not_drafting_error import PlanNotDraftingError
from task_planner.workflow.make_plan.split_plan.save_graph.saved_graph import SavedGraph
from task_planner.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft


def save_graph(
    plan_id: int,
    drafts: tuple[NodeDraft, ...],
    edges: tuple[EdgeDraft, ...],
    reader: PlanApiReader,
    writer: PlanApiWriter,
) -> SavedGraph:
    """앞선 시도의 노드를 지우고, 노드를 저장해 서버 id 를 받고, 그 id 로 간선을 저장한다."""
    removed_node_count = _clear_previous_nodes(plan_id, reader, writer)
    node_ids = _save_nodes(plan_id, drafts, writer)
    _save_edges(plan_id, edges, node_ids, writer)
    return SavedGraph(node_ids=node_ids, edge_count=len(edges), removed_node_count=removed_node_count)


def _clear_previous_nodes(plan_id: int, reader: PlanApiReader, writer: PlanApiWriter) -> int:
    """작성 중인 계획이면 남아 있는 노드를 지운다 (닿은 간선도 함께 지워진다). 작성 중이 아니면 멈춘다."""
    plan = reader.get_plan(plan_id)
    if plan.status is not PlanStatus.DRAFTING:
        raise PlanNotDraftingError(
            f"계획 {plan_id} 는 작성 중이 아니라({plan.status.value}) 노드를 다시 만들지 않습니다"
        )
    for node in plan.nodes:
        writer.delete_node(plan_id, node.node_id)
    return len(plan.nodes)


def _save_nodes(plan_id: int, drafts: tuple[NodeDraft, ...], writer: PlanApiWriter) -> dict[str, int]:
    """트리 순서대로 저장하고 local_id → 서버 id 표를 돌려준다."""
    node_ids: dict[str, int] = {}
    for draft in drafts:
        new_node = NewNode(
            title=draft.title,
            kind=draft.kind,
            persona_ids=draft.persona_ids,
            output_spec=_real_line_breaks(draft.output_spec),
        )
        node_ids[draft.local_id] = writer.add_node(plan_id, new_node).node_id
    return node_ids


def _save_edges(plan_id: int, edges: tuple[EdgeDraft, ...], node_ids: dict[str, int], writer: PlanApiWriter) -> None:
    for edge in edges:
        writer.add_edge(plan_id, node_ids[edge.from_local_id], node_ids[edge.to_local_id])


def _real_line_breaks(text: str) -> str:
    """모델이 줄바꿈을 글자 '\\n' 으로 낸 것을 실제 줄바꿈으로 바꾼다 (사용자, 2026-11-19)."""
    return text.replace("\\n", "\n")
