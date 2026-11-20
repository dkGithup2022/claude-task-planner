from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.persona.persona_read import PersonaRead


class PersonaResponse(BaseModel):
    persona_id: int = Field(description="페르소나 id", examples=[1])
    name: str = Field(description="이름", examples=["dankim-persona"])
    description: str = Field(description="설명")
    memory_count: int = Field(description="이 페르소나를 쓰는 지식 수")
    plan_count: int = Field(description="이 페르소나를 쓰는 계획 수 (참여 또는 노드 담당)")

    @classmethod
    def from_read(cls, read: PersonaRead) -> Self:
        return cls(
            persona_id=read.persona_id,
            name=read.name,
            description=read.description,
            memory_count=read.memory_count,
            plan_count=read.plan_count,
        )


class PersonaListResponse(BaseModel):
    personas: list[PersonaResponse] = Field(description="persona_id 순")
