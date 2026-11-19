"""plan_run 워크플로 선언 (D 계획 실행). 계획서: specs/plans/workflow-plan_run.md

지금은 묶음 1 (find_plan, start_run, resume) 까지와 시험용 임시 끝 단계(wip_notice)다.
묶음 2~5 를 만들며 prompts, rounds, finish_plan, notify 를 더한다.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.plan_run import has_broken, not_stopped, was_running  # noqa: F401
from task_plan_manager.workflow.plan_run.find_plan import find_plan_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.apply_rerun import apply_rerun_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.ask_rerun import ask_rerun_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.check_broken import check_broken_task  # noqa: F401
from task_plan_manager.workflow.plan_run.start_run import start_run_task  # noqa: F401
from task_plan_manager.workflow.plan_run.wip_notice import wip_notice_task  # noqa: F401

PLAN_RUN_FLOW = FlowDefinition(
    name="plan_run",
    description="승인된 계획의 노드를 간선 순서대로 실행한다",
    root=group("plan_run", ChildRun.IN_ORDER,
        task("find_plan", PerformedBy.CODE, Ref("plan_run.find_plan")),
        task("start_run", PerformedBy.CODE, Ref("plan_run.start_run"), reads=("find_plan",)),
        group("resume", ChildRun.IN_ORDER,
            task("check_broken", PerformedBy.CODE, Ref("plan_run.check_broken"), reads=("find_plan",)),
            task("ask_rerun", PerformedBy.MAIN_SESSION_ASK, Ref("plan_run.ask_rerun"),
                 run_if=Ref("plan_run.has_broken"), reads=("check_broken",)),
            task("apply_rerun", PerformedBy.CODE, Ref("plan_run.apply_rerun"),
                 run_if=Ref("plan_run.has_broken"), reads=("find_plan", "check_broken", "ask_rerun")),
            run_if=Ref("plan_run.was_running"), reads=("start_run",)),
        task("wip_notice", PerformedBy.MAIN_SESSION_SHOW, Ref("plan_run.wip_notice"),
             reads=("find_plan", "check_broken", "apply_rerun"))),
)  # fmt: skip
