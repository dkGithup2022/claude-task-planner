from abc import ABC, abstractmethod

from task_plan_server.model.persona.persona import Persona
from task_plan_server.model.persona.persona_identity import PersonaIdentity

from .dto.persona_create_command import PersonaCreateCommand
from .dto.persona_update_command import PersonaUpdateCommand


class PersonaWriter(ABC):
    @abstractmethod
    def create(self, command: PersonaCreateCommand) -> PersonaIdentity:
        """새 페르소나. 같은 이름이 있으면 PersonaNameDuplicatedException."""

    @abstractmethod
    def update(self, command: PersonaUpdateCommand) -> Persona:
        """이름·설명 가운데 값이 있는 것만 바꾼다. 없으면 404, 다른 페르소나와 이름이 같으면 409."""

    @abstractmethod
    def delete(self, identity: PersonaIdentity) -> None:
        """페르소나를 지운다. 없으면 404. 쓰는 곳 검사는 부르는 쪽(Usecase)이 한다."""
