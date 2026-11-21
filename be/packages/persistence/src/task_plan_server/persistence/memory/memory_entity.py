from datetime import datetime
from typing import Self

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Index, Text, false, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_source import MemorySource
from task_plan_server.persistence.base import Base, utcnow
from task_plan_server.persistence.enum_column import value_enum

from .memory_persona_entity import MemoryPersonaEntity
from .memory_source_entity import MemorySourceEntity


class MemoryEntity(Base):
    __tablename__ = "memories"
    __table_args__ = (Index("ix_memories_search_tokens", "search_tokens", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    kind: Mapped[MemoryKind] = mapped_column(value_enum(MemoryKind), nullable=False)
    theme: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # 검색용 낱말 (작업 이름 무게 A, 본문 무게 B). 도메인에는 없다. 저장할 때 repository 가 넣는다.
    # 지식을 읽을 때는 쓰지 않으므로 늦게 읽는다 (deferred)
    search_tokens: Mapped[str] = deferred(
        mapped_column(TSVECTOR, nullable=False, server_default=text("''::tsvector"))
    )

    personas: Mapped[list[MemoryPersonaEntity]] = relationship(
        lazy="selectin", cascade="all, delete-orphan", order_by="MemoryPersonaEntity.position"
    )
    sources: Mapped[list[MemorySourceEntity]] = relationship(
        lazy="selectin", cascade="all, delete-orphan", order_by="MemorySourceEntity.position"
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

    def to_domain(self) -> Memory:
        return Memory(
            self.id,
            self.kind,
            self.theme,
            self.body,
            tuple(persona.persona_id for persona in self.personas),
            tuple(MemorySource(source.quote, source.plan_id) for source in self.sources),
            self.created_at,
            self.updated_at,
        )

    @classmethod
    def from_domain(cls, domain: Memory) -> Self:
        return cls(
            id=domain.memory_id,
            kind=domain.kind,
            theme=domain.theme,
            body=domain.body,
            personas=to_memory_persona_entities(domain.persona_ids),
            sources=to_memory_source_entities(domain.sources),
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


def to_memory_persona_entities(persona_ids: tuple[int, ...]) -> list[MemoryPersonaEntity]:
    return [
        MemoryPersonaEntity(persona_id=persona_id, position=position)
        for position, persona_id in enumerate(persona_ids)
    ]


def to_memory_source_entities(sources: tuple[MemorySource, ...]) -> list[MemorySourceEntity]:
    return [
        MemorySourceEntity(quote=source.quote, plan_id=source.plan_id, position=position)
        for position, source in enumerate(sources)
    ]
