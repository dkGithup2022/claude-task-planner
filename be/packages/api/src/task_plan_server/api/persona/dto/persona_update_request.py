from pydantic import BaseModel, Field


class PersonaUpdateRequest(BaseModel):
    """바꿀 필드만 보낸다. 빠지거나 null 이면 그대로 둔다."""

    name: str | None = Field(default=None, min_length=1, max_length=255, description="이름")
    description: str | None = Field(default=None, description="설명")
