"""plan_run 워크플로 선언 (D 계획 실행). 계획서: specs/plans/workflow-plan_run.md

지금은 묶음 1 (find_plan, start_run, resume), 묶음 2 (prompts) 까지와 시험용 임시 끝 단계(wip_notice)다.
묶음 3~5 를 만들며 rounds, finish_plan, notify 를 더한다.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.plan_run import (  # noqa: F401
    has_broken,
    has_failed_prompts,
    has_missing_prompts,
    not_stopped,
    was_running,
)
from task_plan_manager.workflow.plan_run.find_plan import find_plan_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.ask_retry import ask_retry_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.count_prompts import count_prompts_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.retry_prompts import retry_prompts_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.show_estimate import show_estimate_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.write_prompts import write_prompts_task  # noqa: F401
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
        group("prompts", ChildRun.IN_ORDER,
            task("count_prompts", PerformedBy.CODE, Ref("plan_run.count_prompts"), reads=("find_plan",)),
            task("show_estimate", PerformedBy.MAIN_SESSION_SHOW, Ref("plan_run.show_estimate"),
                 run_if=Ref("plan_run.has_missing_prompts"), reads=("count_prompts",)),
            task("write_prompts", PerformedBy.CODE, Ref("plan_run.write_prompts"),
                 run_if=Ref("plan_run.has_missing_prompts"), reads=("find_plan", "count_prompts")),
            task("ask_retry", PerformedBy.MAIN_SESSION_ASK, Ref("plan_run.ask_retry"),
                 run_if=Ref("plan_run.has_failed_prompts"), reads=("write_prompts",)),
            task("retry_prompts", PerformedBy.CODE, Ref("plan_run.retry_prompts"),
                 run_if=Ref("plan_run.has_failed_prompts"), reads=("find_plan", "write_prompts", "ask_retry")),
            run_if=Ref("plan_run.not_stopped", {"upto": "resume"}), reads=("check_broken", "apply_rerun")),
        task("wip_notice", PerformedBy.MAIN_SESSION_SHOW, Ref("plan_run.wip_notice"),
             reads=("find_plan", "check_broken", "apply_rerun", "write_prompts", "retry_prompts"))),
)  # fmt: skip
