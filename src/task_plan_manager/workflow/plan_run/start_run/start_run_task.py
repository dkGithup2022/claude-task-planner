"""start_run: 승인된 계획을 실행 중으로 바꾼다. 이미 실행 중이면 바꾸지 않고 이어 가기로 표시한다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.workflow.plan_run.show_progress import show_run_started


@TASKS.register_as("plan_run.start_run")
class StartRunTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 승인이면 실행 중으로 바꾼다. 이미 실행 중이면 그대로 두고 이어 가기로 표시한다
        found = context.read("find_plan")
        was_running = PlanStatus(found["status"]) is PlanStatus.RUNNING
        if not was_running:
            plan_api_writer().set_plan_status(found["plan_id"], PlanStatus.RUNNING)
        show_run_started(plan_api_reader().get_plan(found["plan_id"]))
        return TaskOutput({"was_running": was_running})
