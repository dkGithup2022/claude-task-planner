from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.service.persona.persona_check import require_personas
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.memory_update_command import MemoryUpdateCommand
from ..memory_writer import MemoryWriter


class MemoryUpdateUsecase:
    """PATCH /api/memories/{memory_id} 의 진입점. 서버는 받은 것을 저장만 한다."""

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
    def execute(self, command: MemoryUpdateCommand) -> MemoryIdentity:
        require_personas(self._persona_repository, command.persona_ids)
        saved = self._memory_writer.update(command)
        assert saved.memory_id is not None
        return MemoryIdentity(saved.memory_id)
