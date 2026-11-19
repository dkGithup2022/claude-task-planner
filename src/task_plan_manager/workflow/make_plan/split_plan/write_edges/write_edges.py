"""3-3 간선. 모든 저장 전 노드를 한 번에 보여 주고 간선을 받는다 (claude -p 1번).
받은 간선은 코드가 정리한다: 쓸 수 없는 간선을 버리고, 순환을 만드는 간선은 넣지 않고,
받는 산출물로 적혔는데 빠진 직접 간선을 더한다. 노드는 바로 이어진 선행 노드의 결과만 읽기 때문이다."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.claude_utils.prompt.call_prompt import call_prompt
from task_plan_manager.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_plan_manager.workflow.make_plan.split_plan.request_md import demoted
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edges_result import EdgesResult
from task_plan_manager.workflow.make_plan.split_plan.write_edges.prompt_edges_output import EdgesOutput
from task_plan_manager.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft

EDGES = PromptSpec(
    name="edges",
    prompt_file=Path(__file__).parent / "prompt_edges.md",
    output_type=EdgesOutput,
    model="opus",
)


def write_edges(
    request_md: str, drafts: tuple[NodeDraft, ...], call_log: PromptCallLog, caller: PromptCaller = call_prompt
) -> EdgesResult:
    """모든 노드를 보고 간선을 받은 뒤, 버릴 것을 버리고 순환 없이 넣고, 빠진 받는 산출물 간선을 더한다."""
    if len(drafts) < 2:
        return EdgesResult(edges=(), warnings=())
    proposed = _ask_edges(request_md, drafts, call_log, caller)
    warnings: list[str] = []
    local_ids = {draft.local_id for draft in drafts}
    edges: list[EdgeDraft] = []
    for edge in proposed:
        _add_if_valid(edges, edge, local_ids, warnings, origin="간선 프롬프트")
    for edge in _prerequisite_edges(drafts):
        if edge not in edges:
            _add_if_valid(edges, edge, local_ids, warnings, origin="받는 산출물")
    return EdgesResult(edges=tuple(edges), warnings=tuple(warnings))


def _ask_edges(
    request_md: str, drafts: tuple[NodeDraft, ...], call_log: PromptCallLog, caller: PromptCaller
) -> list[EdgeDraft]:
    output, record = caller(EDGES, build_edges_input(request_md, drafts))
    call_log.save("edges", record)
    return list(output.edges)


def _prerequisite_edges(drafts: tuple[NodeDraft, ...]) -> list[EdgeDraft]:
    """정의서에서 받는 산출물로 적힌 작업마다 직접 간선 하나."""
    return [
        EdgeDraft(from_local_id=prerequisite.local_id, to_local_id=draft.local_id)
        for draft in drafts
        for prerequisite in draft.prerequisites
    ]


def _add_if_valid(
    edges: list[EdgeDraft], edge: EdgeDraft, local_ids: set[str], warnings: list[str], origin: str
) -> None:
    """없는 작업, 자기 자신, 중복, 순환을 만드는 간선은 넣지 않고 경고한다. 나머지는 edges 에 더한다."""
    label = f"{origin}의 간선 {edge.from_local_id} → {edge.to_local_id}"
    if edge.from_local_id not in local_ids or edge.to_local_id not in local_ids:
        warnings.append(f"{label}: 작업 목록에 없는 local_id 라 버림")
    elif edge.from_local_id == edge.to_local_id:
        warnings.append(f"{label}: 자기 자신을 잇는 간선이라 버림")
    elif edge in edges:
        warnings.append(f"{label}: 이미 있는 간선이라 버림")
    elif _reaches(edges, start=edge.to_local_id, goal=edge.from_local_id):
        warnings.append(f"{label}: 넣으면 순환이 생겨 넣지 않음")
    else:
        edges.append(edge)


def _reaches(edges: list[EdgeDraft], start: str, goal: str) -> bool:
    """start 에서 간선을 따라가 goal 에 닿는지. 닿으면 goal → start 간선이 순환을 만든다."""
    seen: set[str] = set()
    waiting = [start]
    while waiting:
        current = waiting.pop()
        if current == goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        waiting += [edge.to_local_id for edge in edges if edge.from_local_id == current]
    return False


def build_edges_input(request_md: str, drafts: tuple[NodeDraft, ...]) -> str:
    """간선 입력: 명령서와, 작업마다 local_id·경로·종류·받는 산출물·산출물."""
    titles = {draft.local_id: draft.title for draft in drafts}
    sections = [
        "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
        "# 작업 목록\n실행되는 작업입니다. 목차의 n 으로 시작하는 값이 작업의 local_id 입니다.",
    ]
    for draft in drafts:
        received = [
            f"  - {item.local_id}({titles.get(item.local_id, '?')}): {item.what}" for item in draft.prerequisites
        ]
        sections.append(
            "\n".join(
                [
                    f"## {draft.local_id}",
                    f"- 경로: {draft.path}",
                    f"- 종류: {draft.kind.value}",
                    "- 받는 산출물:",
                    "\n".join(received) or "  (없음)",
                    "- 산출물:",
                    _product_part(draft.output_spec),
                ]
            )
        )
    return "\n\n".join(sections)


def _product_part(output_spec: str) -> str:
    """output_spec 에서 '### 산출물' 절의 글만."""
    after = output_spec.split("### 산출물\n", 1)[-1]
    return after.split("\n\n### 그 외 설명", 1)[0].strip()
