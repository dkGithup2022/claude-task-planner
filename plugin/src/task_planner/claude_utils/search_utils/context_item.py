"""ContextItem: 관계있는지 고를 컨텍스트 하나 (검색 결과 하나)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContextItem:
    context_id: int  # 고른 결과로 돌려받을 id (지식이면 지식 id)
    title: str  # 컨텍스트의 제목 (지식이면 작업 이름)
    body: str  # 본문 전체
