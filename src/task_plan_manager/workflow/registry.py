"""워크플로 이름 → FlowDefinition. start <이름> 이 여기서 찾는다. 새 워크플로를 만들면 여기 추가한다."""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.workflow.confirm_plan.confirm_plan_flows import PLAN_CANCEL_FLOW, PLAN_GO_FLOW
from task_plan_manager.workflow.count_joke.count_joke_flow import COUNT_JOKE_FLOW
from task_plan_manager.workflow.demo.demo_flow import DEMO_FLOW
from task_plan_manager.workflow.list_plans.list_plans_flow import LIST_PLANS_FLOW
from task_plan_manager.workflow.make_plan.make_plan_flow import MAKE_PLAN_FLOW
from task_plan_manager.workflow.plan_run.plan_run_flow import PLAN_RUN_FLOW

FLOWS: dict[str, FlowDefinition] = {
    "demo": DEMO_FLOW,
    "count_joke": COUNT_JOKE_FLOW,
    "make_plan": MAKE_PLAN_FLOW,
    "list_plans": LIST_PLANS_FLOW,
    "plan_go": PLAN_GO_FLOW,
    "plan_cancel": PLAN_CANCEL_FLOW,
    "plan_run": PLAN_RUN_FLOW,
}
