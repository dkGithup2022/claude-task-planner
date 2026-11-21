from pydantic import BaseModel, Field

from task_plan_server.model.memory.memory_kind import MemoryKind


class MemorySearchRequest(BaseModel):
    kind: MemoryKind = Field(description="이 종류의 지식만")
    query: str = Field(description="검색어")
    persona_ids: list[int] = Field(description="이 페르소나 가운데 하나라도 겹치는 지식만")
    theme: str | None = Field(default=None, description="주면 이 작업 이름의 지식만")
    limit: int = Field(default=10, ge=1, le=30, description="최대 개수")
