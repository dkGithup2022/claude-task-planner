from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_kind import MemoryKind

from .source_item import SourceItem


class MemoryCreateRequest(BaseModel):
    kind: MemoryKind = Field(description="knowledge | attitude | plan")
    theme: str = Field(min_length=1, description="작업 이름")
    body: str = Field(min_length=1, description="본문 md")
    persona_ids: list[int] = Field(description="적용할 페르소나 id")
    source: list[SourceItem] = Field(description="근거 목록")
