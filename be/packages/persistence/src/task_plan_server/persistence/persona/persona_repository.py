from task_plan_server.exception.persona.persona_not_found_exception import PersonaNotFoundException
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.persona.persona import Persona
from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.model.persona.persona_read import PersonaRead
from task_plan_server.transaction import TransactionManager, transactional

from .persona_entity import PersonaEntity
from .persona_entity_query import PersonaEntityQuery
from .persona_join_query import PersonaJoinQuery, PersonaWithCountsRow


class DefaultPersonaRepository(PersonaRepository):
    def __init__(
        self, tx: TransactionManager, entities: PersonaEntityQuery, joins: PersonaJoinQuery
    ) -> None:
        self.tx = tx
        self._entities = entities
        self._joins = joins

    @transactional
    def find_all(self) -> list[PersonaRead]:
        return [_to_read(row) for row in self._joins.find_all_with_counts()]

    @transactional
    def save(self, persona: Persona) -> Persona:
        if persona.persona_id is None:
            entity = self._entities.add(PersonaEntity.from_domain(persona))
        else:
            found = self._entities.get(persona.persona_id)
            if found is None:
                raise PersonaNotFoundException(f"persona not found: {persona.persona_id}")
            entity = found
            entity.name = persona.name
            entity.description = persona.description
            entity.updated_at = persona.updated_at
            self._entities.flush()
        return entity.to_domain()

    @transactional
    def exists_by_name(self, name: str, exclude: PersonaIdentity | None) -> bool:
        exclude_id = exclude.persona_id if exclude is not None else None
        return self._entities.exists_by_name_and_active(name, exclude_id)

    @transactional
    def find_write_by_id(self, identity: PersonaIdentity) -> Persona | None:
        entity = self._entities.find_by_id_and_active(identity.persona_id)
        return entity.to_domain() if entity is not None else None

    @transactional
    def find_by_id(self, identity: PersonaIdentity) -> PersonaRead | None:
        row = self._joins.find_by_id_with_counts(identity.persona_id)
        return _to_read(row) if row is not None else None

    @transactional
    def delete_by_id(self, identity: PersonaIdentity) -> None:
        entity = self._entities.get(identity.persona_id)
        if entity is None or entity.is_deleted:
            return
        entity.soft_delete()
        self._entities.flush()

    @transactional
    def find_missing_ids(self, persona_ids: list[int]) -> list[int]:
        found = self._entities.find_active_ids_in(persona_ids)
        return [persona_id for persona_id in dict.fromkeys(persona_ids) if persona_id not in found]


def _to_read(row: PersonaWithCountsRow) -> PersonaRead:
    persona = Persona(row.id, row.name, row.description, row.created_at, row.updated_at)
    return persona.to_read(memory_count=row.memory_count, plan_count=row.plan_count)
