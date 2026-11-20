from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Index, String, Text, false, text
from sqlalchemy.orm import Mapped, mapped_column

from task_plan_server.model.persona.persona import Persona
from task_plan_server.persistence.base import Base, utcnow


class PersonaEntity(Base):
    __tablename__ = "personas"
    # 이름은 지우지 않은 페르소나 사이에서만 유일하다. 지운 페르소나의 이름은 다시 쓸 수 있다
    __table_args__ = (
        Index(
            "uq_personas_name_active",
            "name",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

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

    def to_domain(self) -> Persona:
        return Persona(self.id, self.name, self.description, self.created_at, self.updated_at)

    @classmethod
    def from_domain(cls, domain: Persona) -> Self:
        return cls(
            id=domain.persona_id,
            name=domain.name,
            description=domain.description,
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
