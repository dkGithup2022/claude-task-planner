from task_plan_server.exception.memory.memory_not_found_exception import MemoryNotFoundException
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.transaction import TransactionManager, transactional

from .memory_entity import MemoryEntity, to_memory_persona_entities, to_memory_source_entities
from .memory_entity_query import MemoryEntityQuery


class DefaultMemoryRepository(MemoryRepository):
    def __init__(self, tx: TransactionManager, entities: MemoryEntityQuery) -> None:
        self.tx = tx
        self._entities = entities

    @transactional
    def save(self, memory: Memory) -> Memory:
        if memory.memory_id is None:
            entity = self._entities.add(MemoryEntity.from_domain(memory))
        else:
            found = self._entities.get(memory.memory_id)
            if found is None:
                raise MemoryNotFoundException(f"memory not found: {memory.memory_id}")
            entity = found
            entity.kind = memory.kind
            entity.theme = memory.theme
            entity.body = memory.body
            current = entity.to_domain()
            # 바뀐 목록만 자식 행을 바꾼다. 보내지 않은 목록을 다시 쓰면 동시에 온 덧붙이기를 덮는다
            if current.persona_ids != memory.persona_ids:
                entity.personas = to_memory_persona_entities(memory.persona_ids)
            if current.sources != memory.sources:
                entity.sources = to_memory_source_entities(memory.sources)
            entity.updated_at = memory.updated_at
            self._entities.flush()
        return entity.to_domain()

    @transactional
    def find_write_by_id(self, identity: MemoryIdentity) -> Memory | None:
        entity = self._entities.find_by_id_and_active(identity.memory_id)
        return entity.to_domain() if entity is not None else None

    @transactional
    def find_by_id(self, identity: MemoryIdentity) -> MemoryRead | None:
        entity = self._entities.find_by_id_and_active(identity.memory_id)
        return entity.to_domain().to_read() if entity is not None else None

    @transactional
    def delete_by_id(self, identity: MemoryIdentity) -> None:
        entity = self._entities.get(identity.memory_id)
        if entity is None or entity.is_deleted:
            return
        entity.soft_delete()
        self._entities.flush()

    @transactional
    def find_by_condition(self, condition: MemoryListCondition) -> list[MemoryRead]:
        entities = self._entities.find_by_condition_and_active(condition)
        return [entity.to_domain().to_read() for entity in entities]

    @transactional
    def count_by_condition(self, condition: MemoryListCondition) -> int:
        return self._entities.count_by_condition_and_active(condition)
