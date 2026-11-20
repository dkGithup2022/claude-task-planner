"""멈춘 뒤의 단계를 건너뛰는 조건: upto 묶음까지에서 멈춘 자리가 없으면 참.
선언 예: Ref("plan_run.not_stopped", {"upto": "resume"}), reads 에 check_broken, apply_rerun."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.run_condition import RunCondition
from task_plan_manager.engine.registry.registries import CONDITIONS
from task_plan_manager.workflow.plan_run.stopped_node import stop_point


@CONDITIONS.register_as("plan_run.not_stopped")
def not_stopped(upto: str) -> RunCondition:
    def check(context: FlowContext) -> bool:
        return stop_point(context, upto) is None

    return check
