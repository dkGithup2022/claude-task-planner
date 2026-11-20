from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_kind import MemoryKind

from .source_item import SourceItem


class MemoryUpdateRequest(BaseModel):
    """바꿀 필드만 보낸다. 빠지거나 null 인 필드는 바꾸지 않는다.

    CLI 의 덧붙이기는 body, source 를, 웹의 수정은 kind, theme, body, persona_ids 를 보낸다.
    """

    kind: MemoryKind | None = Field(default=None, description="knowledge | attitude | plan")
    theme: str | None = Field(default=None, min_length=1, description="작업 이름")
    body: str | None = Field(default=None, min_length=1, description="고친 본문 전체 md")
    persona_ids: list[int] | None = Field(default=None, description="적용할 페르소나 id")
    source: list[SourceItem] | None = Field(default=None, description="고친 근거 목록 전체")
