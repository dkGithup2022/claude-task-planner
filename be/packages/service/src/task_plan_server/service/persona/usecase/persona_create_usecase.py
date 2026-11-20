from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.persona_create_command import PersonaCreateCommand
from ..persona_writer import PersonaWriter


class PersonaCreateUsecase:
    """POST /api/personas 의 진입점. 같은 이름이면 409."""

    def __init__(self, tx: TransactionManager, persona_writer: PersonaWriter) -> None:
        self.tx = tx
        self._persona_writer = persona_writer

    @transactional
    def execute(self, command: PersonaCreateCommand) -> PersonaIdentity:
        return self._persona_writer.create(command)
