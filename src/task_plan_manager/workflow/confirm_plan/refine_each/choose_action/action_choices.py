"""choose_action 의 선택지 만들기와 답 읽기. 선택 창은 선택지가 4 개까지라 덧붙이기는 기존 지식 두 개까지다."""

from __future__ import annotations

import re
from typing import Any

NEW = "새 지식으로 저장"
SKIP = "넣지 않기"
APPEND_PREFIX = "덧붙이기: "
_APPEND_ID = re.compile(r"^덧붙이기: #(\d+) ")
MAX_APPEND_TARGETS = 2


def action_choices(existing: list[dict[str, Any]]) -> tuple[str, ...]:
    """새로 저장, 점수 높은 기존 지식 두 개에 덧붙이기, 넣지 않기. 기존 지식이 없으면 두 개."""
    appends = [f"{APPEND_PREFIX}#{memory['memory_id']} {memory['theme']}" for memory in existing[:MAX_APPEND_TARGETS]]
    return (NEW, *appends, SKIP)


def append_target_id(answer: str) -> int | None:
    """답이 덧붙이기면 그 기존 지식의 id, 아니면 None."""
    matched = _APPEND_ID.match(answer)
    return int(matched.group(1)) if matched else None
