from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition

from .memory_entity import MemoryEntity
from .memory_persona_entity import MemoryPersonaEntity


class MemoryEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id_and_active(self, id: int) -> MemoryEntity | None:
        stmt = select(MemoryEntity).where(MemoryEntity.id == id, MemoryEntity.is_deleted.is_(False))
        return self._session.scalar(stmt)

    def get(self, id: int) -> MemoryEntity | None:
        return self._session.get(MemoryEntity, id)

    def add(self, entity: MemoryEntity) -> MemoryEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def flush(self) -> None:
        self._session.flush()

    def find_for_search_and_active(
        self, kind: MemoryKind, persona_ids: list[int], theme: str | None
    ) -> list[MemoryEntity]:
        """검색 대상. kind 가 같고 페르소나가 겹치고, theme 을 주면 작업 이름이 같은 지식."""
        if not persona_ids:
            return []
        overlapping = select(MemoryPersonaEntity.memory_id).where(
            MemoryPersonaEntity.persona_id.in_(persona_ids)
        )
        stmt = select(MemoryEntity).where(
            MemoryEntity.kind == kind,
            MemoryEntity.id.in_(overlapping),
            MemoryEntity.is_deleted.is_(False),
        )
        if theme is not None:
            stmt = stmt.where(MemoryEntity.theme == theme)
        return list(self._session.scalars(stmt.order_by(MemoryEntity.updated_at.desc())).all())

    def find_by_condition_and_active(self, condition: MemoryListCondition) -> list[MemoryEntity]:
        stmt = _where_condition(select(MemoryEntity), condition).order_by(
            MemoryEntity.updated_at.desc(), MemoryEntity.id.desc()
        )
        if condition.limit is not None:
            stmt = stmt.limit(condition.limit)
        return list(self._session.scalars(stmt).all())

    def count_by_condition_and_active(self, condition: MemoryListCondition) -> int:
        stmt = _where_condition(select(func.count()).select_from(MemoryEntity), condition)
        return int(self._session.scalar(stmt) or 0)


def _where_condition[T](stmt: Select[T], condition: MemoryListCondition) -> Select[T]:
    """웹 목록의 동적 조건. 비운 조건은 붙이지 않는다. 검색어의 % 와 _ 는 글자 그대로 찾는다."""
    stmt = stmt.where(MemoryEntity.is_deleted.is_(False))
    if condition.query:
        stmt = stmt.where(
            or_(
                MemoryEntity.theme.icontains(condition.query, autoescape=True),
                MemoryEntity.body.icontains(condition.query, autoescape=True),
            )
        )
    if condition.kind is not None:
        stmt = stmt.where(MemoryEntity.kind == condition.kind)
    if condition.persona_id is not None:
        using = select(MemoryPersonaEntity.memory_id).where(
            MemoryPersonaEntity.persona_id == condition.persona_id
        )
        stmt = stmt.where(MemoryEntity.id.in_(using))
    return stmt
