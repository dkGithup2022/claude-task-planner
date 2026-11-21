"""make_plan 워크플로 선언. 계획서: specs/plans/workflow-make_plan.md

interview → write_request → register_plan → split_plan → prepare_show → show_plan.
"""

from __future__ import annotations

from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.make_plan.interview import interview_task  # noqa: F401
from task_planner.workflow.make_plan.prepare_show import prepare_show_task  # noqa: F401
from task_planner.workflow.make_plan.register_plan import register_plan_task  # noqa: F401
from task_planner.workflow.make_plan.show_plan import show_plan_task  # noqa: F401
from task_planner.workflow.make_plan.split_plan import split_plan_task  # noqa: F401
from task_planner.workflow.make_plan.write_request import write_request_task  # noqa: F401

MAKE_PLAN_FLOW = FlowDefinition(
    name="make_plan",
    description="사용자를 인터뷰해 명령서를 정리하고 계획을 만들어 보인다",
    root=group("make_plan", ChildRun.IN_ORDER,
        task("interview", PerformedBy.MAIN_SESSION_TALK, Ref("make_plan.interview")),
        task("write_request", PerformedBy.CLAUDE_P, Ref("make_plan.write_request"), reads=("interview",)),
        task("register_plan", PerformedBy.CODE, Ref("make_plan.register_plan"), reads=("write_request",)),
        task("split_plan", PerformedBy.CODE, Ref("make_plan.split_plan"), reads=("register_plan",)),
        task("prepare_show", PerformedBy.CODE, Ref("make_plan.prepare_show"),
             reads=("interview", "register_plan", "split_plan")),
        task("show_plan", PerformedBy.MAIN_SESSION_SHOW, Ref("make_plan.show_plan"),
             reads=("register_plan", "prepare_show"))),
)  # fmt: skip
