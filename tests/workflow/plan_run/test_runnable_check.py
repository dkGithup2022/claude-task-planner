import pytest

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError
from task_plan_manager.workflow.plan_run.find_plan.runnable_check import require_runnable


def _plan(status: PlanStatus) -> Plan:
    return Plan(7, "계획", "# 명령", (1,), status, "2026-11-19T00:00:00Z", (), ())


@pytest.mark.parametrize("status", [PlanStatus.APPROVED, PlanStatus.RUNNING])
def test_should_pass_approved_and_running(status):
    require_runnable(_plan(status))


@pytest.mark.parametrize(
    ("status", "message"),
    [
        (PlanStatus.DRAFTING, "작성 중 상태라 실행할 수 없습니다. 계획을 다 만든 뒤 /task_plan_manager:plan-go 7"),
        (PlanStatus.REVIEWING, "검토 중 상태라 실행할 수 없습니다. 확정은 /task_plan_manager:plan-go 7"),
        (PlanStatus.REJECTED, "계획 7 은 불허 상태라 실행할 수 없습니다"),
        (PlanStatus.DONE, "계획 7 은 끝남 상태입니다"),
    ],
)
def test_should_stop_with_status_message(status, message):
    with pytest.raises(PlanNotRunnableError, match=message):
        require_runnable(_plan(status))
