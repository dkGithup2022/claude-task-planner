"""멈춘 뒤의 단계를 건너뛰는 조건: 이번 실행에서 사용자가 멈추기를 고르지 않았으면 참."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS
from task_plan_manager.workflow.plan_run.stopped_node import stopped_nodes


@CONDITIONS.register_as("plan_run.not_stopped")
def not_stopped() -> RunCondition:
    def check(context: FlowContext) -> bool:
        return not stopped_nodes(context)

    return check
