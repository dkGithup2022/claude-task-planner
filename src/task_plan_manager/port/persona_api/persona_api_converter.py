"""GET /personas 응답 JSON → Persona. mock 파일도 같은 모양이라 같이 쓴다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.model.persona.persona import Persona


class PersonaApiConverter:
    def to_personas(self, body: dict[str, Any]) -> tuple[Persona, ...]:
        return tuple(self.to_persona(item) for item in body.get("personas") or ())

    def to_persona(self, item: dict[str, Any]) -> Persona:
        return Persona(persona_id=int(item["persona_id"]), name=item["name"], description=item.get("description") or "")
