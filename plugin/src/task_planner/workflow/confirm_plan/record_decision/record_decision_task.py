"""record_decision: 검토 중인 계획을 선언이 정한 결정(plan_go 는 승인, plan_cancel 은 불허)으로 바꾼다.
결정 값은 선언의 Ref args 로 받는다. 이유는 받지 않는다 (사용자, 2026-11-18)."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_planner.workflow.confirm_plan.record_decision.decision_not_allowed_error import DecisionNotAllowedError
from task_planner.workflow.confirm_plan.show_progress import show_decision
from task_planner.workflow.list_plans.show_plans.plan_status_label import status_label


@TASKS.register_as("confirm_plan.record_decision")
class RecordDecisionTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def __init__(self, decision: str) -> None:
        self.decision = PlanStatus(decision)  # approved | rejected (선언의 Ref args)

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 검토 중인 계획을 선언이 정한 결정(승인 / 불허)으로 바꾼다
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        if not plan.status.can_move_to(self.decision):
            raise DecisionNotAllowedError(
                f"계획 {plan_id} 은 {status_label(plan.status.value)} 상태라 다시 확정할 수 없습니다"
            )
        plan_api_writer().set_plan_status(plan_id, self.decision)
        show_decision(plan_id, self.decision, len(plan.nodes))
        return TaskOutput({"plan_id": plan_id, "status": self.decision.value})
