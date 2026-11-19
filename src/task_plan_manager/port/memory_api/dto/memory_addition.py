"""기존 지식에 덧붙이기 요청 (POST /memories/{memory_id}/append)."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.memory.memory_source import MemorySource


@dataclass(frozen=True, slots=True)
class MemoryAddition:
    body: str
    sources: tuple[MemorySource, ...]
