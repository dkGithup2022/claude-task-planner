from abc import ABC, abstractmethod

from task_plan_server.model.persona.persona_read import PersonaRead


class PersonaReader(ABC):
    @abstractmethod
    def get_all(self) -> list[PersonaRead]:
        """지우지 않은 페르소나 전부. persona_id 순. 없으면 []."""
