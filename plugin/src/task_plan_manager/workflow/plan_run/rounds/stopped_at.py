"""continue_notice, confirm, failed 의 조건: 같은 차례의 run_nodes 가 그 자리에서 멈췄으면 참."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS


@CONDITIONS.register_as("plan_run.stopped_at")
def stopped_at(value: str) -> RunCondition:
    def check(context: FlowContext) -> bool:
        return bool(context.read("run_nodes")["stop_at"] == value)

    return check
