from pydantic import BaseModel, Field


class PlanCreateRequest(BaseModel):
    title: str = Field(min_length=1, description="계획 제목")
    request: str = Field(description="명령서 md")
    persona_ids: list[int] = Field(description="참여 페르소나 id")
