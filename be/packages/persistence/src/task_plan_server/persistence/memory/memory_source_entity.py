from sqlalchemy import BigInteger, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from task_plan_server.persistence.base import Base


class MemorySourceEntity(Base):
    """지식의 근거 하나. 부모(memories)와 생애주기가 같아 공통 4컬럼이 없다."""

    __tablename__ = "memory_sources"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("memories.id"), nullable=False, index=True
    )
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    plan_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # 근거 목록 안의 순서
