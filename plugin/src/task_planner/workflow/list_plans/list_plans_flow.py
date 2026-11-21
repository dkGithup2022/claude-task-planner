"""list_plans 워크플로 선언. 계획서: specs/plans/workflow-list_plans.md

/plan-go, /plan-cancel, /plan-run 을 계획 id 없이 불렀을 때 이 작업 폴더의 계획 목록을 보이고 끝낸다.
"""

from __future__ import annotations

from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.list_plans.collect_plans import collect_plans_task  # noqa: F401
from task_planner.workflow.list_plans.show_plans import show_plans_task  # noqa: F401

LIST_PLANS_FLOW = FlowDefinition(
    name="list_plans",
    description="이 작업 폴더의 계획 목록(id, 제목, 상태)을 보이고, id 를 넣어 다시 부르라고 안내한다",
    root=group("list_plans", ChildRun.IN_ORDER,
        task("collect_plans", PerformedBy.CODE, Ref("list_plans.collect_plans")),
        task("show_plans", PerformedBy.MAIN_SESSION_SHOW, Ref("list_plans.show_plans"), reads=("collect_plans",))),
)  # fmt: skip
