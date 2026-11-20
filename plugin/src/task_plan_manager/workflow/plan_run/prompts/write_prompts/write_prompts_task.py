"""write_prompts (D 2): count_prompts 가 고른 노드마다 작업 지시를 만든다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.workflow.plan_run.prompts.write_prompts.write_node_prompts import write_node_prompts


@TASKS.register_as("plan_run.write_prompts")
class WritePromptsTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 읽기: 만들 노드 (count_prompts 가 고른 것) → 만들기·쓰기 (write_node_prompts)
        plan_id = context.read("find_plan")["plan_id"]
        targets = [int(node["node_id"]) for node in context.read("count_prompts")["missing"]]
        made, failed = write_node_prompts(plan_id, targets)
        return TaskOutput({"made": made, "failed": failed})
