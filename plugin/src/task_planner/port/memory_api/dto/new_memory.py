"""지식 만들기 요청 (POST /memories)."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.memory.memory_kind import MemoryKind
from task_planner.model.memory.memory_source import MemorySource


@dataclass(frozen=True, slots=True)
class NewMemory:
    kind: MemoryKind
    theme: str
    body: str
    persona_ids: tuple[int, ...]
    sources: tuple[MemorySource, ...]
