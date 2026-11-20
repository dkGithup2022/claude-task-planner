from sqlalchemy import select
from sqlalchemy.orm import Session

from .plan_node_entity import PlanNodeEntity


class PlanNodeEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_plan_id_and_active(self, plan_id: int) -> list[PlanNodeEntity]:
        stmt = (
            select(PlanNodeEntity)
            .where(PlanNodeEntity.plan_id == plan_id, PlanNodeEntity.is_deleted.is_(False))
            .order_by(PlanNodeEntity.id)
        )
        return list(self._session.scalars(stmt).all())

    def find_by_id_and_active(self, id: int) -> PlanNodeEntity | None:
        stmt = select(PlanNodeEntity).where(
            PlanNodeEntity.id == id, PlanNodeEntity.is_deleted.is_(False)
        )
        return self._session.scalar(stmt)

    def get(self, id: int) -> PlanNodeEntity | None:
        return self._session.get(PlanNodeEntity, id)

    def add(self, entity: PlanNodeEntity) -> PlanNodeEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def flush(self) -> None:
        self._session.flush()
