"""계획 상태로 실행할 수 있는지 본다. 승인(처음 실행)과 실행 중(이어 가기)만 실행한다 (사용자, D 섹션 판정)."""

from __future__ import annotations

from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError

# 실행하지 않는 상태마다 사용자에게 보일 글. {id} 에 계획 id 가 들어간다
NOT_RUNNABLE = {
    PlanStatus.DRAFTING: (
        "계획 {id} 은 작성 중 상태라 실행할 수 없습니다. 계획을 다 만든 뒤 /task-planner:plan-go {id} 로 확정해 주세요"
    ),
    PlanStatus.REVIEWING: "계획 {id} 은 검토 중 상태라 실행할 수 없습니다. 확정은 /task-planner:plan-go {id}",
    PlanStatus.REJECTED: "계획 {id} 은 불허 상태라 실행할 수 없습니다",
    PlanStatus.DONE: "계획 {id} 은 끝남 상태입니다. 모든 노드를 이미 실행했습니다",
}


def require_runnable(plan: Plan) -> None:
    """승인·실행 중이 아니면 상태에 맞는 글로 PlanNotRunnableError."""
    message = NOT_RUNNABLE.get(plan.status)
    if message is not None:
        raise PlanNotRunnableError(message.format(id=plan.plan_id))
