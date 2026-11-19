"""ask_rerun, apply_rerun 의 조건: check_broken 이 결과 파일 없이 끊긴 노드를 하나라도 찾았으면 참."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS


@CONDITIONS.register_as("plan_run.has_broken")
def has_broken() -> RunCondition:
    def check(context: FlowContext) -> bool:
        return bool(context.read("check_broken")["nodes"])

    return check
