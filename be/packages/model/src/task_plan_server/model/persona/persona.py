from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from task_plan_server.model.audit import utcnow

from .persona_read import PersonaRead


@dataclass(frozen=True, slots=True)
class Persona:
    """작업을 맡는 역할. 이름은 페르소나마다 다르다."""

    persona_id: int | None
    name: str  # 예: dankim-persona, be-developer
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, description: str) -> Self:
        now = utcnow()
        return cls(None, name, description, now, now)

    def with_profile(self, name: str, description: str) -> Self:
        """이름과 설명을 바꾼 새 페르소나. 바꾸지 않는 필드는 부르는 쪽이 지금 값으로 채운다."""
        return replace(self, name=name, description=description, updated_at=utcnow())

    def to_read(self, memory_count: int, plan_count: int) -> PersonaRead:
        """지식 수와 계획 수는 부르는 쪽이 세어서 넘긴다."""
        if self.persona_id is None:
            raise ValueError("persona must be persisted before to_read")
        return PersonaRead(
            self.persona_id,
            self.name,
            self.description,
            memory_count,
            plan_count,
            self.created_at,
            self.updated_at,
        )
