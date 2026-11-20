from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PersonaIdentity:
    persona_id: int
