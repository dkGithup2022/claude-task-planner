from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PersonaRead:
    persona_id: int
    name: str
    description: str
    memory_count: int  # 이 페르소나를 쓰는 지식 수
    plan_count: int  # 이 페르소나를 쓰는 계획 수
    created_at: datetime
    updated_at: datetime
