from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.api.common.time_format import to_utc_text
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.model.plan.plan_status import PlanStatus


class PlanCreateResponse(BaseModel):
    plan_id: int = Field(description="계획 id", examples=[11])
    status: PlanStatus = Field(description="계획 상태. 만들 때는 drafting")
    created_at: str = Field(description="만든 시각 (UTC)", examples=["2026-11-20T04:16:15Z"])

    @classmethod
    def from_read(cls, read: PlanRead) -> Self:
        return cls(
            plan_id=read.plan_id, status=read.status, created_at=to_utc_text(read.created_at)
        )
