from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_read import MemoryRead

from .source_item import SourceItem


class MemoryResponse(BaseModel):
    """지식 하나. API 문서의 GET /memories/{memory_id} 모양."""

    memory_id: int = Field(description="지식 id", examples=[1])
    kind: MemoryKind = Field(description="knowledge | attitude | plan")
    theme: str = Field(description="작업 이름")
    body: str = Field(description="본문 md. 덧붙임 머리가 들어 있을 수 있다")
    persona_ids: list[int] = Field(description="적용할 페르소나 id")
    source: list[SourceItem] = Field(description="근거 목록 (덧붙인 순서)")

    @classmethod
    def from_read(cls, read: MemoryRead) -> Self:
        return cls(
            memory_id=read.memory_id,
            kind=read.kind,
            theme=read.theme,
            body=read.body,
            persona_ids=list(read.persona_ids),
            source=[SourceItem.from_source(source) for source in read.sources],
        )
