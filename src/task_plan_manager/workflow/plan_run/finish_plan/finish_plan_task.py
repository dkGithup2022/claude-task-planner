"""finish_plan (D 6): 모든 노드가 완료나 건너뜀이면 계획 상태를 실행 중에서 끝남으로 바꾼다 (흐름 도식 D 6)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.plan.plan_schedule import plan_progress
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer


@TASKS.register_as("plan_run.finish_plan")
class FinishPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 읽기: 계획과 노드 상태
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        # 판단: 모든 노드가 완료·건너뜀인지
        finished = plan_progress(plan).finished
        # 쓰기: 끝났고 아직 실행 중이면 끝남으로. 이미 끝남이면 쓰지 않는다
        if finished and plan.status is PlanStatus.RUNNING:
            plan_api_writer().set_plan_status(plan_id, PlanStatus.DONE)
        return TaskOutput({"finished": finished})
