"""병합할 지식 목록을 선택 창의 쪽으로 나눈다. 선택 창에는 선택지가 2~4 개 들어간다.
한 쪽에 셋과 "다음 3개 보기"를 두고, 남은 것이 넷 이하가 되면 마지막 쪽에 다 보인다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

PAGE_SIZE = 3  # 한 쪽에 보일 지식 수. 넷째 자리는 "다음 3개 보기"
LAST_PAGE_SIZE = PAGE_SIZE + 1  # 마지막 쪽에는 넷까지
NEXT_PAGE = "다음 3개 보기"


def page_of(existing: list[dict[str, Any]], page: int) -> list[dict[str, Any]]:
    """page 쪽(1 부터)에 보일 지식."""
    rest = existing[(page - 1) * PAGE_SIZE :]
    return rest if len(rest) <= LAST_PAGE_SIZE else rest[:PAGE_SIZE]


def has_next(existing: list[dict[str, Any]], page: int) -> bool:
    """page 쪽 뒤에 쪽이 더 있는가."""
    return len(existing) - (page - 1) * PAGE_SIZE > LAST_PAGE_SIZE


def page_range(existing: list[dict[str, Any]], page: int) -> str:
    """질문에 붙일 범위. 예: "4~6 / 10"."""
    start = (page - 1) * PAGE_SIZE + 1
    end = start + len(page_of(existing, page)) - 1
    return f"{start}~{end} / {len(existing)}" if end > start else f"{start} / {len(existing)}"
