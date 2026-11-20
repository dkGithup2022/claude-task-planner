from sqlalchemy import select
from sqlalchemy.orm import Session

from task_plan_server.model.plan.plan_status import PlanStatus

from .plan_entity import PlanEntity


class PlanEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id_and_active(self, id: int) -> PlanEntity | None:
        stmt = select(PlanEntity).where(PlanEntity.id == id, PlanEntity.is_deleted.is_(False))
        return self._session.scalar(stmt)

    def get(self, id: int) -> PlanEntity | None:
        return self._session.get(PlanEntity, id)

    def add(self, entity: PlanEntity) -> PlanEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def flush(self) -> None:
        self._session.flush()

    def find_all_and_active(self, status: PlanStatus | None, limit: int | None) -> list[PlanEntity]:
        stmt = select(PlanEntity).where(PlanEntity.is_deleted.is_(False))
        if status is not None:
            stmt = stmt.where(PlanEntity.status == status)
        stmt = stmt.order_by(PlanEntity.created_at.desc(), PlanEntity.id.desc())
        if limit is not None:
            stmt = stmt.limit(limit)
        return list(self._session.scalars(stmt).all())
