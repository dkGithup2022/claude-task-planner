from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, false
from sqlalchemy.orm import Mapped, mapped_column

from task_plan_server.model.plan_edge.plan_edge import PlanEdge
from task_plan_server.persistence.base import Base, utcnow


class PlanEdgeEntity(Base):
    """계획 간선. 계획·노드와 다른 aggregate 라 id 를 값으로만 갖는다."""

    __tablename__ = "plan_edges"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    plan_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    from_node_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    to_node_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    def to_domain(self) -> PlanEdge:
        return PlanEdge(
            self.id,
            self.plan_id,
            self.from_node_id,
            self.to_node_id,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: PlanEdge) -> Self:
        return cls(
            id=domain.edge_id,
            plan_id=domain.plan_id,
            from_node_id=domain.from_node_id,
            to_node_id=domain.to_node_id,
            is_deleted=False,
            deleted_at=None,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def soft_delete(self) -> None:
        now = utcnow()
        self.is_deleted = True
        self.deleted_at = now
        self.updated_at = now
