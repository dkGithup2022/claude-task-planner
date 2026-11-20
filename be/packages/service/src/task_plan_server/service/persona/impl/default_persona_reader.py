from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.persona.persona_read import PersonaRead

from ..persona_reader import PersonaReader


class DefaultPersonaReader(PersonaReader):
    def __init__(self, repository: PersonaRepository) -> None:
        self._repository = repository

    def get_all(self) -> list[PersonaRead]:
        return self._repository.find_all()
