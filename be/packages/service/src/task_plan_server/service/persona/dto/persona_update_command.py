from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PersonaUpdateCommand:
    """None 인 필드는 바꾸지 않는다."""

    persona_id: int
    name: str | None = None
    description: str | None = None
