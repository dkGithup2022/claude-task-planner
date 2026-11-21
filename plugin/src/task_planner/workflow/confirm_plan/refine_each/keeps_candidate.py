"""keep_each 묶음의 조건: choose_action 의 답이 "넣지 않기"가 아니면 그 후보를 계속 다룬다 (사용자, 2026-11-19).
engine 의 기본 조건 answer_is 는 같은지만 보므로, 아닌지를 보는 조건을 따로 둔다."""

from __future__ import annotations

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.run_condition import RunCondition
from task_planner.engine.registry.registries import CONDITIONS
from task_planner.workflow.confirm_plan.refine_each.choose_action.action_choices import SKIP


@CONDITIONS.register_as("confirm_plan.keeps_candidate")
def keeps_candidate() -> RunCondition:
    def check(context: FlowContext) -> bool:
        return bool(context.read("choose_action")["answer"] != SKIP)

    return check
