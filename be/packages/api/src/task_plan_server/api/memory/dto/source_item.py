from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_source import MemorySource


class SourceItem(BaseModel):
    """지식의 근거 하나. 요청과 응답에 같이 쓴다."""

    quote: str = Field(description="사용자가 한 말")
    plan_id: int = Field(description="그 말이 나온 계획 id", examples=[11])

    def to_source(self) -> MemorySource:
        return MemorySource(self.quote, self.plan_id)

    @classmethod
    def from_source(cls, source: MemorySource) -> Self:
        return cls(quote=source.quote, plan_id=source.plan_id)
