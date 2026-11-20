from task_plan_server.exception.persona.persona_in_use_exception import PersonaInUseException
from task_plan_server.exception.persona.persona_not_found_exception import PersonaNotFoundException
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..persona_writer import PersonaWriter


class PersonaDeleteUsecase:
    """DELETE /api/personas/{persona_id} 의 진입점.

    쓰는 지식이나 계획(참여 또는 노드 담당)이 있으면 PersonaInUseException(409) 으로 막는다.
    """

    def __init__(
        self,
        tx: TransactionManager,
        persona_repository: PersonaRepository,
        persona_writer: PersonaWriter,
    ) -> None:
        self.tx = tx
        self._persona_repository = persona_repository
        self._persona_writer = persona_writer

    @transactional
    def execute(self, identity: PersonaIdentity) -> None:
        read = self._persona_repository.find_by_id(identity)
        if read is None:
            raise PersonaNotFoundException(f"persona not found: {identity.persona_id}")
        if read.memory_count > 0 or read.plan_count > 0:
            raise PersonaInUseException(identity.persona_id, read.memory_count, read.plan_count)
        self._persona_writer.delete(identity)
