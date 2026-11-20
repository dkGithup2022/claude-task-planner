from dataclasses import dataclass

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_source import MemorySource


@dataclass(frozen=True, slots=True)
class MemoryCreateCommand:
    kind: MemoryKind
    theme: str  # 작업 이름
    body: str  # md. CLI 가 만든 그대로 저장한다
    persona_ids: tuple[int, ...]
    sources: tuple[MemorySource, ...]
