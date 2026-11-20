from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from .persona_entity import PersonaEntity


class PersonaEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, id: int) -> PersonaEntity | None:
        return self._session.get(PersonaEntity, id)

    def exists_by_name_and_active(self, name: str, exclude_id: int | None) -> bool:
        condition = exists().where(PersonaEntity.name == name, PersonaEntity.is_deleted.is_(False))
        if exclude_id is not None:
            condition = condition.where(PersonaEntity.id != exclude_id)
        return bool(self._session.scalar(select(condition)))

    def add(self, entity: PersonaEntity) -> PersonaEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def flush(self) -> None:
        self._session.flush()

    def find_by_id_and_active(self, id: int) -> PersonaEntity | None:
        stmt = select(PersonaEntity).where(
            PersonaEntity.id == id, PersonaEntity.is_deleted.is_(False)
        )
        return self._session.scalar(stmt)

    def find_active_ids_in(self, ids: list[int]) -> set[int]:
        if not ids:
            return set()
        stmt = select(PersonaEntity.id).where(
            PersonaEntity.id.in_(ids), PersonaEntity.is_deleted.is_(False)
        )
        return set(self._session.scalars(stmt).all())
