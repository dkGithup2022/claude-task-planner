"""ask_retry, retry_prompts 의 조건: write_prompts 가 돌았고 작업 지시를 만들지 못한 노드가 있으면 참."""

from __future__ import annotations

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.run_condition import RunCondition
from task_planner.engine.definition.task.output_missing_error import OutputMissingError
from task_planner.engine.registry.registries import CONDITIONS


@CONDITIONS.register_as("plan_run.has_failed_prompts")
def has_failed_prompts() -> RunCondition:
    def check(context: FlowContext) -> bool:
        try:
            return bool(context.read("write_prompts")["failed"])
        except OutputMissingError:  # 만들 노드가 없어 write_prompts 를 건너뜀
            return False

    return check
