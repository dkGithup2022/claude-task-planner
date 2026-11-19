"""간선 다시 정하기: 바뀐 노드와 앞뒤 노드 사이의 간선을 claude -p(opus)가 정의서를 읽고 다시 정한다.
계획을 처음 만들 때(make_plan 의 간선 정리)와 대화로 고칠 때(plan edit)가 같이 쓴다 (사용자, 2026-11-19).
받은 간선은 코드가 한 번 거른다. 범위 밖 노드, 자기 자신, 중복, 사용자가 끊은 간선, 순환을 만드는 간선은 버리고,
사용자가 이은 간선은 먼저 넣는다."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from task_plan_manager.claude_utils.prompt.call_prompt import call_prompt
from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_plan_manager.workflow.relink_edges.prompt_relink_edges_output import RelinkEdgesOutput
from task_plan_manager.workflow.relink_edges.relink_input import build_relink_input
from task_plan_manager.workflow.relink_edges.relink_request import Edge, RelinkRequest

RELINK_EDGES = PromptSpec(
    name="relink_edges",
    prompt_file=Path(__file__).parent / "prompt_relink_edges.md",
    output_type=RelinkEdgesOutput,
    model="opus",
)

PromptCaller = Callable[[PromptSpec, str], tuple[Any, PromptCallRecord]]  # 실제로는 call_prompt, 시험에서는 가짜


@dataclass(frozen=True, slots=True)
class RelinkResult:
    edges: tuple[Edge, ...]  # 바뀐 노드와 앞뒤 노드 사이의 간선 전부 (거른 뒤)
    dropped: tuple[tuple[Edge, str], ...]  # 버린 간선과 그 까닭. 글은 부른 쪽이 노드 이름으로 만든다
    record: PromptCallRecord  # claude -p 호출 기록. make_plan 은 실행 기록에 남긴다


def relink_edges(request: RelinkRequest, caller: PromptCaller = call_prompt) -> RelinkResult:
    """claude -p 를 한 번 부르고 받은 간선을 거른다. 호출이 실패하면 PromptCallError 를 그대로 올린다."""
    output: RelinkEdgesOutput
    output, record = caller(RELINK_EDGES, build_relink_input(request))
    proposed = [(edge.from_id, edge.to_id) for edge in output.edges]
    edges, dropped = _filter(proposed, request)
    return RelinkResult(tuple(edges), tuple(dropped), record)


def _filter(proposed: list[Edge], request: RelinkRequest) -> tuple[list[Edge], list[tuple[Edge, str]]]:
    """쓸 수 없는 간선은 버리고 까닭과 함께 남긴다.
    그대로 남는 간선과 사용자가 이은 간선은 먼저 넣어 순환 검사에서 밀리지 않게 한다."""
    scope = request.scope_ids()
    unlinked = set(request.user_unlinks)
    kept = [*request.fixed_edges, *request.user_links]
    edges: list[Edge] = list(dict.fromkeys(edge for edge in kept if edge[0] in scope and edge[1] in scope))
    dropped: list[tuple[Edge, str]] = []
    for edge in proposed:
        reason = _drop_reason(edge, edges, scope, unlinked, request.outside_edges)
        if reason is None:
            edges.append(edge)
        elif edge not in kept:  # 그대로 남는 간선이나 사용자가 이은 간선이 다시 오면 알리지 않는다
            dropped.append((edge, reason))
    return edges, dropped


def _drop_reason(
    edge: Edge, edges: list[Edge], scope: set[int], unlinked: set[Edge], outside: tuple[Edge, ...]
) -> str | None:
    """간선을 버리는 까닭. 넣어도 되면 None. 순환은 범위 밖 노드를 거치는 길까지 본다."""
    from_id, to_id = edge
    if from_id not in scope or to_id not in scope:
        return "바뀐 노드와 앞뒤 노드가 아닌 노드라 버림"
    if from_id == to_id:
        return "자기 자신을 잇는 간선이라 버림"
    if edge in edges:
        return "이미 있는 간선이라 버림"
    if edge in unlinked:
        return "사용자가 끊은 간선이라 버림"
    if _reaches([*edges, *outside], start=to_id, goal=from_id):
        return "넣으면 순환이 생겨 넣지 않음"
    return None


def _reaches(edges: list[Edge], start: int, goal: int) -> bool:
    """start 에서 간선을 따라가 goal 에 닿는지. 닿으면 goal → start 간선이 순환을 만든다."""
    seen: set[int] = set()
    waiting = [start]
    while waiting:
        current = waiting.pop()
        if current == goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        waiting += [to_id for from_id, to_id in edges if from_id == current]
    return False
