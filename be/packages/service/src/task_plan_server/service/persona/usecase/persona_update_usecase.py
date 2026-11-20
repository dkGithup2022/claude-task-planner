from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.persona_update_command import PersonaUpdateCommand
from ..persona_writer import PersonaWriter


class PersonaUpdateUsecase:
    """PATCH /api/personas/{persona_id} 의 진입점."""

    def __init__(self, tx: TransactionManager, persona_writer: PersonaWriter) -> None:
        self.tx = tx
        self._persona_writer = persona_writer

    @transactional
    def execute(self, command: PersonaUpdateCommand) -> PersonaIdentity:
        saved = self._persona_writer.update(command)
        assert saved.persona_id is not None
        return PersonaIdentity(saved.persona_id)
