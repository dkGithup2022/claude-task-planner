from dataclasses import dataclass

from task_plan_server.model.plan.plan_status import PlanStatus


@dataclass(frozen=True, slots=True)
class PlanStatusChangeCommand:
    """계획 상태 바꾸기. 바꾸는 순서는 검사하지 않는다."""

    plan_id: int
    status: PlanStatus
