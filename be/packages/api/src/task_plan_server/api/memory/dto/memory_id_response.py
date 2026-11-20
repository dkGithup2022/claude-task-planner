from pydantic import BaseModel, Field


class MemoryIdResponse(BaseModel):
    """만들기·고치기 응답. CLI 는 memory_id 만 읽는다."""

    memory_id: int = Field(description="지식 id", examples=[7])
