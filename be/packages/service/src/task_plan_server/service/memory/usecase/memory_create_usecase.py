from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.service.persona.persona_check import require_personas
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.memory_create_command import MemoryCreateCommand
from ..memory_writer import MemoryWriter


class MemoryCreateUsecase:
    """POST /api/memories 의 진입점."""

    def __init__(
        self,
        tx: TransactionManager,
        memory_writer: MemoryWriter,
        persona_repository: PersonaRepository,
    ) -> None:
        self.tx = tx
        self._memory_writer = memory_writer
        self._persona_repository = persona_repository

    @transactional
    def execute(self, command: MemoryCreateCommand) -> MemoryIdentity:
        require_personas(self._persona_repository, command.persona_ids)
        return self._memory_writer.create(command)
