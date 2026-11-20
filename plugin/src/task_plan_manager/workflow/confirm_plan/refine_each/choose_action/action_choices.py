"""choose_action 의 선택지: 병합 / 새 지식으로 저장 / 넣지 않기. 비슷한 지식이 없으면 병합은 뺀다.
병합할 지식은 다음 단계(choose_target)에서 고른다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

MERGE = "병합"
NEW = "새 지식으로 저장"
SKIP = "넣지 않기"


def action_choices(existing: list[dict[str, Any]]) -> tuple[str, ...]:
    """비슷한 지식이 있으면 병합까지 셋, 없으면 새로 저장과 넣지 않기 둘."""
    return (MERGE, NEW, SKIP) if existing else (NEW, SKIP)
