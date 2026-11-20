from sqlalchemy import BigInteger, ForeignKey, Identity, Integer
from sqlalchemy.orm import Mapped, mapped_column

from task_plan_server.persistence.base import Base


class MemoryPersonaEntity(Base):
    """지식을 적용할 페르소나 하나. 부모(memories)와 생애주기가 같아 공통 4컬럼이 없다."""

    __tablename__ = "memory_personas"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("memories.id"), nullable=False, index=True
    )
    persona_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # persona_ids 안의 순서
