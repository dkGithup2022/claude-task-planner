from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemorySource:
    """지식의 근거. 사용자가 한 말과 그 말이 나온 계획."""

    quote: str
    plan_id: int
