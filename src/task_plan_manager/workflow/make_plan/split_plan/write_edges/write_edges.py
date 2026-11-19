"""3-3 간선. 저장 전 노드 전부를 간선 다시 정하기(relink_edges)에 넘기고 간선을 받는다 (claude -p 1번).
처음 만들 때라 모든 노드가 바뀐 노드이고, 앞뒤 노드는 없다. 정의서의 받는 산출물로 만든 간선을 이전 간선으로 넘긴다.
저장 전 노드의 local_id("n1" 같은 글자)는 1, 2, 3… 으로 바꿔 넘기고 받은 간선을 다시 local_id 로 되돌린다."""

from __future__ import annotations

from task_plan_manager.claude_utils.prompt.call_prompt import call_prompt
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edges_result import EdgesResult
from task_plan_manager.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft
from task_plan_manager.workflow.relink_edges.relink_edges import relink_edges
from task_plan_manager.workflow.relink_edges.relink_node import RelinkNode
from task_plan_manager.workflow.relink_edges.relink_request import RelinkRequest


def write_edges(
    drafts: tuple[NodeDraft, ...], call_log: PromptCallLog, caller: PromptCaller = call_prompt
) -> EdgesResult:
    """모든 노드를 보고 간선을 받는다. 거르기(없는 노드, 자기 자신, 중복, 순환)는 relink_edges 가 한다."""
    if len(drafts) < 2:
        return EdgesResult(edges=(), warnings=())
    number_of = {draft.local_id: number for number, draft in enumerate(drafts, 1)}
    local_id_of = {number: local_id for local_id, number in number_of.items()}
    result = relink_edges(_relink_request(drafts, number_of), caller)
    call_log.save("edges", result.record)
    edges = tuple(EdgeDraft(local_id_of[from_id], local_id_of[to_id]) for from_id, to_id in result.edges)
    warnings = tuple(
        f"간선 프롬프트의 간선 {local_id_of.get(from_id, from_id)} → {local_id_of.get(to_id, to_id)}: {reason}"
        for (from_id, to_id), reason in result.dropped
    )
    return EdgesResult(edges=edges, warnings=warnings)


def _relink_request(drafts: tuple[NodeDraft, ...], number_of: dict[str, int]) -> RelinkRequest:
    """저장 전 노드 전부를 바뀐 노드로. 받는 산출물(prerequisites)로 적힌 간선이 이전 간선이다."""
    nodes = tuple(
        RelinkNode(number_of[draft.local_id], draft.title, draft.kind.value, draft.output_spec) for draft in drafts
    )
    previous = tuple(
        (number_of[prerequisite.local_id], number_of[draft.local_id])
        for draft in drafts
        for prerequisite in draft.prerequisites
        if prerequisite.local_id in number_of
    )
    return RelinkRequest(
        change=f"계획을 처음 만듦: 노드 {len(drafts)}개",
        original_nodes=(),
        changed_nodes=nodes,
        neighbor_nodes=(),
        previous_edges=previous,
    )
