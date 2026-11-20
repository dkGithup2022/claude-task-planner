from dataclasses import dataclass
from datetime import datetime

from .memory_kind import MemoryKind
from .memory_source import MemorySource


@dataclass(frozen=True, slots=True)
class MemoryRead:
    memory_id: int
    kind: MemoryKind
    theme: str
    body: str
    persona_ids: tuple[int, ...]
    sources: tuple[MemorySource, ...]
    appended_count: int  # 본문에 덧붙임 머리가 나온 횟수
    source_plan_ids: tuple[int, ...]  # 근거가 나온 계획. 처음 나온 순서, 겹치지 않음
    created_at: datetime
    updated_at: datetime
