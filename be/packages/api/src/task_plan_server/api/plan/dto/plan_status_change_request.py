from pydantic import BaseModel, Field

from task_plan_server.model.plan.plan_status import PlanStatus


class PlanStatusChangeRequest(BaseModel):
    status: PlanStatus = Field(description="바꿀 상태. 순서는 검사하지 않는다")
