"""run_nodes (D 3): 바깥 차례마다 우리 루프를 돌린다. 멈춤 표시가 이번 실행의 것이면 바로 돌아온다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.workflow.plan_run.rounds.run_nodes.run_until_question import run_until_question


@TASKS.register_as("plan_run.run_nodes")
class RunNodesTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        plan_id = context.read("find_plan")["plan_id"]
        return TaskOutput(run_until_question(plan_id, context.state.run_id))
