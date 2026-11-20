from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.api.common.time_format import to_utc_text
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.service.memory.dto.memory_list import MemoryList


class MemoryListItem(BaseModel):
    """목록의 한 줄. 본문은 넣지 않는다 (조회 화면이 GET /{memory_id} 로 읽는다)."""

    memory_id: int = Field(description="지식 id", examples=[7])
    kind: MemoryKind = Field(description="knowledge | attitude | plan")
    theme: str = Field(description="작업 이름")
    persona_ids: list[int] = Field(description="적용할 페르소나 id")
    appended_count: int = Field(description="덧붙인 횟수")
    source_plan_ids: list[int] = Field(description="근거가 나온 계획 id (처음 나온 순서)")
    created_at: str = Field(description="만든 시각 (UTC)", examples=["2026-11-20T04:39:00Z"])
    updated_at: str = Field(description="고친 시각 (UTC)")
    edited: bool = Field(description="만든 뒤 고친 적이 있으면 true (메인의 '고침')")

    @classmethod
    def from_read(cls, read: MemoryRead) -> Self:
        return cls(
            memory_id=read.memory_id,
            kind=read.kind,
            theme=read.theme,
            persona_ids=list(read.persona_ids),
            appended_count=read.appended_count,
            source_plan_ids=list(read.source_plan_ids),
            created_at=to_utc_text(read.created_at),
            updated_at=to_utc_text(read.updated_at),
            edited=read.updated_at != read.created_at,
        )


class MemoryListResponse(BaseModel):
    items: list[MemoryListItem] = Field(description="고친 시각 최근 순")
    total: int = Field(description="limit 을 빼고 조건에 맞는 개수")

    @classmethod
    def from_list(cls, memory_list: MemoryList) -> Self:
        return cls(
            items=[MemoryListItem.from_read(read) for read in memory_list.items],
            total=memory_list.total,
        )
