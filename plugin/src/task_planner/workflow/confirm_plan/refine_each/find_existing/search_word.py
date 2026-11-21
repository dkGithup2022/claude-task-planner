"""기존 지식 찾기의 검색어."""

from __future__ import annotations

from typing import Any


def build_search_word(candidate: dict[str, Any]) -> str:
    """지식 후보로 비슷한 기존 지식을 찾을 검색어: 작업 이름과 내용 전체."""
    return f"{candidate['theme']} {candidate['content']}"
