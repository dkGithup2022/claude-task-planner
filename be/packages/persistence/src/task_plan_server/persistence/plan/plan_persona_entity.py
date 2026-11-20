from sqlalchemy import BigInteger, ForeignKey, Identity, Integer
from sqlalchemy.orm import Mapped, mapped_column

from task_plan_server.persistence.base import Base


class PlanPersonaEntity(Base):
    """계획의 참여 페르소나 하나. 부모(plans)와 생애주기가 같아 감사·soft-delete 컬럼이 없다."""

    __tablename__ = "plan_personas"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    plan_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("plans.id"), nullable=False, index=True
    )
    persona_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # persona_ids 안의 순서
