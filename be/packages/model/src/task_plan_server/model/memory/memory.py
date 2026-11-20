from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from task_plan_server.model.audit import utcnow

from .memory_kind import MemoryKind
from .memory_read import MemoryRead
from .memory_source import MemorySource

# CLI 의 Memory.append 가 덧붙일 때 다는 머리의 앞부분. 뒤에 번호와 별표가 붙는다.
# 서버는 이 머리를 세기만 하고 만들거나 고치지 않는다.
APPENDED_MARK_PREFIX = "****** KNOWLEDGE APPENDED "


@dataclass(frozen=True, slots=True)
class Memory:
    """작업할 때 쓰는 지식 하나. 본문과 근거는 CLI 가 만든 그대로 저장한다."""

    memory_id: int | None
    kind: MemoryKind
    theme: str  # 작업 이름
    body: str  # md
    persona_ids: tuple[int, ...]  # 적용할 페르소나
    sources: tuple[MemorySource, ...]  # 근거. 덧붙일 때마다 뒤에 붙는다
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        kind: MemoryKind,
        theme: str,
        body: str,
        persona_ids: tuple[int, ...],
        sources: tuple[MemorySource, ...],
    ) -> Self:
        now = utcnow()
        return cls(None, kind, theme, body, persona_ids, sources, now, now)

    def with_update(
        self,
        kind: MemoryKind,
        theme: str,
        body: str,
        persona_ids: tuple[int, ...],
        sources: tuple[MemorySource, ...],
    ) -> Self:
        """값을 바꾼 새 지식. 바꾸지 않는 필드는 부르는 쪽이 지금 값으로 채운다."""
        return replace(
            self,
            kind=kind,
            theme=theme,
            body=body,
            persona_ids=persona_ids,
            sources=sources,
            updated_at=utcnow(),
        )

    def to_read(self) -> MemoryRead:
        if self.memory_id is None:
            raise ValueError("memory must be persisted before to_read")
        return MemoryRead(
            self.memory_id,
            self.kind,
            self.theme,
            self.body,
            self.persona_ids,
            self.sources,
            self.body.count(APPENDED_MARK_PREFIX),
            tuple(dict.fromkeys(source.plan_id for source in self.sources)),
            self.created_at,
            self.updated_at,
        )
