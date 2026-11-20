"""지식의 근거 하나: 사용자가 한 말과 그 말이 나온 계획."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemorySource:
    quote: str
    plan_id: int
