import logging

from task_plan_server.exception.memory.memory_not_found_exception import MemoryNotFoundException
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.memory_create_command import MemoryCreateCommand
from ..dto.memory_update_command import MemoryUpdateCommand
from ..memory_writer import MemoryWriter

logger = logging.getLogger(__name__)


class DefaultMemoryWriter(MemoryWriter):
    def __init__(self, tx: TransactionManager, repository: MemoryRepository) -> None:
        self.tx = tx
        self._repository = repository

    @transactional
    def create(self, command: MemoryCreateCommand) -> MemoryIdentity:
        memory = Memory.create(
            command.kind, command.theme, command.body, command.persona_ids, command.sources
        )
        saved = self._repository.save(memory)
        assert saved.memory_id is not None
        logger.info("Memory created: id=%s, kind=%s", saved.memory_id, saved.kind)
        return MemoryIdentity(saved.memory_id)

    @transactional
    def update(self, command: MemoryUpdateCommand) -> Memory:
        existing = self._repository.find_write_by_id(MemoryIdentity(command.memory_id))
        if existing is None:
            raise MemoryNotFoundException(f"memory not found: {command.memory_id}")
        updated = existing.with_update(
            kind=_or(command.kind, existing.kind),
            theme=_or(command.theme, existing.theme),
            body=_or(command.body, existing.body),
            persona_ids=_or(command.persona_ids, existing.persona_ids),
            sources=_or(command.sources, existing.sources),
        )
        saved = self._repository.save(updated)
        logger.info("Memory updated: id=%s", saved.memory_id)
        return saved

    @transactional
    def delete(self, identity: MemoryIdentity) -> None:
        if self._repository.find_write_by_id(identity) is None:
            raise MemoryNotFoundException(f"memory not found: {identity.memory_id}")
        self._repository.delete_by_id(identity)
        logger.info("Memory deleted: id=%s", identity.memory_id)


def _or[T](value: T | None, current: T) -> T:
    """보낸 값이 있으면 그 값, 없으면 지금 값."""
    return current if value is None else value
