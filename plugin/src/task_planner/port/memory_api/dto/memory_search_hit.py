"""지식 검색 결과 하나. 검색 응답에는 페르소나와 근거가 없고 점수가 있어 model(Memory)이 아니라 dto 로 둔다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.memory.memory_kind import MemoryKind


@dataclass(frozen=True, slots=True)
class MemorySearchHit:
    memory_id: int
    kind: MemoryKind
    theme: str
    body: str
    score: float
