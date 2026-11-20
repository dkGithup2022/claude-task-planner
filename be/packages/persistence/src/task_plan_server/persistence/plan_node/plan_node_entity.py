from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Text, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_plan_server.model.plan_node.node_kind import NodeKind
from task_plan_server.model.plan_node.plan_node import PlanNode
from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus
from task_plan_server.persistence.base import Base, utcnow
from task_plan_server.persistence.enum_column import value_enum

from .plan_node_persona_entity import PlanNodePersonaEntity


class PlanNodeEntity(Base):
    """계획 노드. 계획과 다른 aggregate 라 plan_id 를 값으로만 갖는다."""

    __tablename__ = "plan_nodes"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    plan_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[NodeKind] = mapped_column(value_enum(NodeKind), nullable=False)
    output_spec: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PlanNodeStatus] = mapped_column(value_enum(PlanNodeStatus), nullable=False)

    personas: Mapped[list[PlanNodePersonaEntity]] = relationship(
        lazy="selectin", cascade="all, delete-orphan", order_by="PlanNodePersonaEntity.position"
    )

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

    def to_domain(self) -> PlanNode:
        return PlanNode(
            self.id,
            self.plan_id,
            self.title,
            self.kind,
            tuple(persona.persona_id for persona in self.personas),
            self.output_spec,
            self.status,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: PlanNode) -> Self:
        return cls(
            id=domain.node_id,
            plan_id=domain.plan_id,
            title=domain.title,
            kind=domain.kind,
            output_spec=domain.output_spec,
            status=domain.status,
            personas=to_node_persona_entities(domain.persona_ids),
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


def to_node_persona_entities(persona_ids: tuple[int, ...]) -> list[PlanNodePersonaEntity]:
    """persona_ids 를 순서를 담은 자식 Entity 로."""
    return [
        PlanNodePersonaEntity(persona_id=persona_id, position=position)
        for position, persona_id in enumerate(persona_ids)
    ]
