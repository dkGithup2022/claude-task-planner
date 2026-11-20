from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PersonaCreateCommand:
    name: str
    description: str
