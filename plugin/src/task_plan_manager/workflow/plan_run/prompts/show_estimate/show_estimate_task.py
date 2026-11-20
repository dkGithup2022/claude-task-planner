"""show_estimate (D 2): 작업 지시를 만들기 전에 노드 수와 대략의 시간·비용을 알린다 (기존 plan-go/procedure.md:51)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest


@TASKS.register_as("plan_run.show_estimate")
class ShowEstimateTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        counted = context.read("count_prompts")
        return ShowRequest(
            f"노드 {len(counted['missing'])}개의 작업 지시를 만듭니다. "
            f"약 {counted['minutes']}분, ${counted['cost_low']}~{counted['cost_high']} 안팎"
        )

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})
