"""페르소나 목록 읽기 (GET /personas)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.persona.persona import Persona


class PersonaApiReader(ABC):
    @abstractmethod
    def list_personas(self) -> tuple[Persona, ...]:
        """모든 페르소나. 없으면 빈 튜플, 서버에서 읽지 못하면 PersonaApiError."""
