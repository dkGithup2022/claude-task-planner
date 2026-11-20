"""show_estimate, write_prompts 의 조건: 작업 지시가 없는 노드가 하나라도 있으면 참."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS


@CONDITIONS.register_as("plan_run.has_missing_prompts")
def has_missing_prompts() -> RunCondition:
    def check(context: FlowContext) -> bool:
        return bool(context.read("count_prompts")["missing"])

    return check
