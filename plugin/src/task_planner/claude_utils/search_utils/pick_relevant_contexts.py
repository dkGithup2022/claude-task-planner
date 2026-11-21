"""검색 결과 가운데 실제 작업과 관계있는 것만 하이쿠로 고른다.

검색어로 찾은 결과에는 관계없는 것이 섞인다. 비싼 프롬프트에 넣기 전에 싼 모델로 걸러,
관계있는 것만 근거로 쓰게 한다 (사용자, 2026-11-21). 지식이나 계획을 모르고 id, 제목, 본문만 다룬다.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.claude_utils.search_utils.context_item import ContextItem
from task_planner.claude_utils.search_utils.prompt_relevant_context_output import RelevantContextOutput

MAX_RELEVANT = 5  # 고르는 컨텍스트의 최대 수

RELEVANT_CONTEXT = PromptSpec(
    name="relevant_context",
    prompt_file=Path(__file__).parent / "prompt_relevant_context.md",
    output_type=RelevantContextOutput,
    model="haiku",
)

# claude -p 를 부르는 함수의 모양. 실제로는 call_prompt, 시험에서는 가짜를 넘긴다
PromptCaller = Callable[[PromptSpec, str], tuple[Any, PromptCallRecord]]


def pick_relevant_contexts(
    task_md: str, items: Sequence[ContextItem], caller: PromptCaller = call_prompt
) -> tuple[tuple[int, ...], PromptCallRecord]:
    """items 가운데 실제 작업과 관계있는 것의 id 를 하이쿠가 고른 중요한 순서로 최대 5 개, 그리고 호출 기록.

    items 에 없는 id 와 겹친 id 는 버린다. 호출이 실패하면 PromptCallError (부르는 쪽이 정한다).
    """
    output, record = caller(RELEVANT_CONTEXT, relevant_context_input(task_md, items))
    return kept_ids(output.ids, items), record


def relevant_context_input(task_md: str, items: Sequence[ContextItem]) -> str:
    """실제 작업 절과 컨텍스트 절. 컨텍스트마다 "## id <id>: <제목>" 줄 아래에 본문 전체."""
    contexts = [f"## id {item.context_id}: {item.title}\n{item.body.strip()}" for item in items]
    return "# 실제 작업\n" + task_md.strip() + "\n\n# 컨텍스트\n" + "\n\n".join(contexts) + "\n"


def kept_ids(ids: list[int], items: Sequence[ContextItem]) -> tuple[int, ...]:
    """하이쿠가 고른 순서대로. items 에 없는 id 와 겹친 id 는 버리고 최대 5 개."""
    known_ids = {item.context_id for item in items}
    return tuple(context_id for context_id in dict.fromkeys(ids) if context_id in known_ids)[:MAX_RELEVANT]
