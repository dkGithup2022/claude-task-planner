from dataclasses import dataclass

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_source import MemorySource


@dataclass(frozen=True, slots=True)
class MemoryUpdateCommand:
    """지식 고치기. None 인 필드는 바꾸지 않는다. 본문과 근거는 받은 그대로 저장한다.

    CLI 의 덧붙이기는 body, sources 만, 웹의 수정은 kind, theme, body, persona_ids 를 보낸다.
    """

    memory_id: int
    kind: MemoryKind | None = None
    theme: str | None = None
    body: str | None = None
    persona_ids: tuple[int, ...] | None = None
    sources: tuple[MemorySource, ...] | None = None
