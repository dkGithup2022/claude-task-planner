"""나누기 판단에 넣을 지식: plan 지식을 10 개 찾고, 하이쿠가 관계있는 것만 최대 5 개 고른 원문.

지식이 나누기 판단의 근거가 되므로 본문은 덧붙임까지 자르지 않고 넣는다 (사용자, 2026-11-21).
검색이 실패하면 "(검색 실패)", 고르기가 실패하면 검색 앞 5 개를 쓰고 경고를 남긴다. 판단은 멈추지 않는다.
"""

from __future__ import annotations

from task_planner.claude_utils.prompt.prompt_call_error import PromptCallError
from task_planner.claude_utils.search_utils.context_item import ContextItem
from task_planner.claude_utils.search_utils.pick_relevant_contexts import MAX_RELEVANT, pick_relevant_contexts
from task_planner.model.memory.memory_kind import MemoryKind
from task_planner.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_planner.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_planner.port.memory_api.memory_api_choice import memory_api_reader
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_planner.workflow.make_plan.split_plan.split_tree.search_word import build_search_word
from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem

CALL_GROUP = "relevant_context"  # 호출 기록 폴더 calls/relevant_context/
NO_KNOWLEDGE = "없음"
SEARCH_FAILED = "(검색 실패)"


def relevant_plan_knowledge(
    plan_title: str,
    work_item: WorkItem,
    persona_ids: tuple[int, ...],
    call_log: PromptCallLog,
    caller: PromptCaller,
) -> tuple[str, str | None]:
    """(나누기 입력의 검색 결과 절에 넣을 글, 경고). 경고가 없으면 None."""
    try:
        hits = search_plan_knowledge(work_item, persona_ids)
    except MemoryApiError as error:
        return SEARCH_FAILED, f"{work_item.name}: 지식 검색 실패 ({error})"
    if not hits:
        return NO_KNOWLEDGE, None
    try:
        picked = pick_relevant_hits(plan_title, work_item, hits, call_log, caller)
    except PromptCallError as error:
        call_log.save(CALL_GROUP, error.record)
        warning = f"{work_item.name}: 관계있는 지식 고르기 실패, 검색 앞 {MAX_RELEVANT}개를 씀 ({error})"
        return found_knowledge_md(hits[:MAX_RELEVANT]), warning
    return found_knowledge_md(picked), None


def search_plan_knowledge(work_item: WorkItem, persona_ids: tuple[int, ...]) -> tuple[MemorySearchHit, ...]:
    """이 작업을 나누는 데 참고할 plan 지식 (작업을 나누는 방식). 검색 기본 개수(10 개)를 받는다."""
    query = MemorySearchQuery(kind=MemoryKind.PLAN, query=build_search_word(work_item), persona_ids=persona_ids)
    return memory_api_reader().search(query)


def pick_relevant_hits(
    plan_title: str,
    work_item: WorkItem,
    hits: tuple[MemorySearchHit, ...],
    call_log: PromptCallLog,
    caller: PromptCaller,
) -> tuple[MemorySearchHit, ...]:
    """검색 결과 가운데 하이쿠가 이 작업과 관계있다고 고른 것만, 고른 순서대로."""
    items = [ContextItem(hit.memory_id, hit.theme, hit.body) for hit in hits]
    picked_ids, record = pick_relevant_contexts(task_md_of(plan_title, work_item), items, caller)
    call_log.save(CALL_GROUP, record)
    hit_by_id = {hit.memory_id: hit for hit in hits}
    return tuple(hit_by_id[memory_id] for memory_id in picked_ids)


def task_md_of(plan_title: str, work_item: WorkItem) -> str:
    """하이쿠에 줄 실제 작업: 계획 제목, 작업 이름, 하는 일."""
    return f"- 계획: {plan_title}\n- 이름: {work_item.name}\n- 하는 일: {work_item.scope}"


def found_knowledge_md(hits: tuple[MemorySearchHit, ...]) -> str:
    """지식마다 "## <작업 이름> (지식 <id>)" 줄 아래에 본문 전체. 없으면 "없음"."""
    if not hits:
        return NO_KNOWLEDGE
    return "\n\n".join(f"## {hit.theme} (지식 {hit.memory_id})\n{hit.body.strip()}" for hit in hits)
