"""페르소나 하나. 계획과 노드, 지식이 persona_ids 로 가리킨다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Persona:
    persona_id: int
    name: str  # 예: dankim-persona, be-developer
    description: str
