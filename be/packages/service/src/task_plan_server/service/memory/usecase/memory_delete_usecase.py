from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..memory_writer import MemoryWriter


class MemoryDeleteUsecase:
    """DELETE /api/memories/{memory_id} 의 진입점. 없는 지식이면 404."""

    def __init__(self, tx: TransactionManager, memory_writer: MemoryWriter) -> None:
        self.tx = tx
        self._memory_writer = memory_writer

    @transactional
    def execute(self, identity: MemoryIdentity) -> None:
        self._memory_writer.delete(identity)
