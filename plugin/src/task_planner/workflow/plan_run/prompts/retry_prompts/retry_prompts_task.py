"""retry_prompts (D 2): 모두 다시 만들기면 실패한 노드의 작업 지시를 한 번 더 만든다. 그래도 실패하면 멈춘다.
멈추기면 만들지 않고 실패한 노드를 그대로 돌려준다 (stop_point 가 멈춘 자리로 읽는다)."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.workflow.plan_run.prompts.retry_choices import STOP
from task_planner.workflow.plan_run.prompts.write_prompts.write_node_prompts import write_node_prompts


@TASKS.register_as("plan_run.retry_prompts")
class RetryPromptsTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 멈추기면 만들지 않는다. 모두 다시 만들기면 실패한 노드만 한 번 더
        failed = context.read("write_prompts")["failed"]
        if context.read("ask_retry")["answer"] == STOP:
            return TaskOutput({"made": [], "failed": failed})
        plan_id = context.read("find_plan")["plan_id"]
        made, still_failed = write_node_prompts(plan_id, [int(node["node_id"]) for node in failed])
        return TaskOutput({"made": made, "failed": still_failed})
