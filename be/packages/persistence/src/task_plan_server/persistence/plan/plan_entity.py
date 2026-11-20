from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Text, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from task_plan_server.model.plan.plan import Plan
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.persistence.base import Base, utcnow
from task_plan_server.persistence.enum_column import value_enum

from .plan_persona_entity import PlanPersonaEntity


class PlanEntity(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    request: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(value_enum(PlanStatus), nullable=False)

    personas: Mapped[list[PlanPersonaEntity]] = relationship(
        lazy="selectin", cascade="all, delete-orphan", order_by="PlanPersonaEntity.position"
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

    def to_domain(self) -> Plan:
        return Plan(
            self.id,
            self.title,
            self.request,
            tuple(persona.persona_id for persona in self.personas),
            self.status,
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: Plan) -> Self:
        return cls(
            id=domain.plan_id,
            title=domain.title,
            request=domain.request,
            status=domain.status,
            personas=to_persona_entities(domain.persona_ids),
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


def to_persona_entities(persona_ids: tuple[int, ...]) -> list[PlanPersonaEntity]:
    """persona_ids 를 순서를 담은 자식 Entity 로."""
    return [
        PlanPersonaEntity(persona_id=persona_id, position=position)
        for position, persona_id in enumerate(persona_ids)
    ]
