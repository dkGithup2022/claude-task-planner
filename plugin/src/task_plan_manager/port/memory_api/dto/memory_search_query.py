"""지식 검색 요청 (POST /memories/search)."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.memory.memory_kind import MemoryKind


@dataclass(frozen=True, slots=True)
class MemorySearchQuery:
    kind: MemoryKind
    query: str
    persona_ids: tuple[int, ...]
    theme: str | None = None  # 주면 그 작업 이름의 지식만
    limit: int = 10
