"""resume 묶음의 조건: 계획이 이미 실행 중이었으면(끊겼다가 다시 부름) 끊긴 노드를 정리한다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS


@CONDITIONS.register_as("plan_run.was_running")
def was_running() -> RunCondition:
    def check(context: FlowContext) -> bool:
        return bool(context.read("start_run")["was_running"])

    return check
