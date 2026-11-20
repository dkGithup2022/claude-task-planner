from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .plan_edge_entity import PlanEdgeEntity


class PlanEdgeEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_plan_id_and_active(self, plan_id: int) -> list[PlanEdgeEntity]:
        stmt = (
            select(PlanEdgeEntity)
            .where(PlanEdgeEntity.plan_id == plan_id, PlanEdgeEntity.is_deleted.is_(False))
            .order_by(PlanEdgeEntity.id)
        )
        return list(self._session.scalars(stmt).all())

    def find_by_node_id_and_active(self, node_id: int) -> list[PlanEdgeEntity]:
        """앞이나 뒤가 이 노드인 간선."""
        stmt = select(PlanEdgeEntity).where(
            or_(PlanEdgeEntity.from_node_id == node_id, PlanEdgeEntity.to_node_id == node_id),
            PlanEdgeEntity.is_deleted.is_(False),
        )
        return list(self._session.scalars(stmt).all())

    def flush(self) -> None:
        self._session.flush()

    def find_by_ends_and_active(
        self, plan_id: int, from_node_id: int, to_node_id: int
    ) -> PlanEdgeEntity | None:
        stmt = (
            select(PlanEdgeEntity)
            .where(
                PlanEdgeEntity.plan_id == plan_id,
                PlanEdgeEntity.from_node_id == from_node_id,
                PlanEdgeEntity.to_node_id == to_node_id,
                PlanEdgeEntity.is_deleted.is_(False),
            )
            .order_by(PlanEdgeEntity.id)
            .limit(1)
        )
        return self._session.scalar(stmt)

    def add(self, entity: PlanEdgeEntity) -> PlanEdgeEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def find_by_id_and_active(self, id: int) -> PlanEdgeEntity | None:
        stmt = select(PlanEdgeEntity).where(
            PlanEdgeEntity.id == id, PlanEdgeEntity.is_deleted.is_(False)
        )
        return self._session.scalar(stmt)

    def get(self, id: int) -> PlanEdgeEntity | None:
        return self._session.get(PlanEdgeEntity, id)
