from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit


class MemorySearchItem(BaseModel):
    memory_id: int = Field(description="지식 id", examples=[6])
    kind: MemoryKind = Field(description="knowledge | attitude | plan")
    theme: str = Field(description="작업 이름")
    body: str = Field(description="본문 md")
    score: float = Field(description="검색어와 가까운 정도. 높을수록 가깝다")

    @classmethod
    def from_hit(cls, hit: MemorySearchHit) -> Self:
        return cls(
            memory_id=hit.memory_id, kind=hit.kind, theme=hit.theme, body=hit.body, score=hit.score
        )


class MemorySearchResponse(BaseModel):
    items: list[MemorySearchItem] = Field(description="점수 높은 순")
