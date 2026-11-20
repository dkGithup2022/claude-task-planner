"""plan_run 워크플로 선언 (D 계획 실행). 계획서: specs/plans/workflow-plan_run.md

지금은 묶음 1 (find_plan, start_run, resume), 묶음 2 (prompts), 묶음 4 (rounds) 까지와 임시 끝 단계(wip_notice)다.
묶음 5 에서 finish_plan, notify 를 더한다.
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
from task_plan_manager.workflow.plan_run.finish_plan import finish_plan_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.ask_retry import ask_retry_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.count_prompts import count_prompts_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.retry_prompts import retry_prompts_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.show_estimate import show_estimate_task  # noqa: F401
from task_plan_manager.workflow.plan_run.prompts.write_prompts import write_prompts_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.apply_rerun import apply_rerun_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.ask_rerun import ask_rerun_task  # noqa: F401
from task_plan_manager.workflow.plan_run.resume.check_broken import check_broken_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds import round_items, stopped_at  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.confirm.ask_confirm import ask_confirm_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.confirm.finish_confirm import finish_confirm_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.confirm.show_confirm import show_confirm_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.continue_notice import continue_notice_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.failed.apply_failed import apply_failed_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.failed.ask_failed import ask_failed_task  # noqa: F401
from task_plan_manager.workflow.plan_run.rounds.run_nodes import run_nodes_task  # noqa: F401
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
        group("rounds", ChildRun.FOR_EACH_ITEM,
            task("run_nodes", PerformedBy.CODE, Ref("plan_run.run_nodes"), reads=("find_plan",)),
            # 노드 실행 차례마다 next 호출을 나누려고 둔 알림 단계다.
            # 메인 세션은 `task_plan_manager next` 를 Bash 로 부르고, 이 호출 하나는 70분이 지나면 강제로 끝난다
            # (plan-run 스킬의 timeout). engine 은 알림·질문 단계를 만나야 next 를 끝내고 메인 세션에 넘긴다.
            # run_nodes 는 30분이 지나면 새 노드를 띄우지 않고, 돌던 노드가 끝나면 "계속"을 돌려준다.
            # 이 단계가 없으면 engine 이 같은 next 안에서 다음 차례를 바로 돌려, next 한 번이 70분을 넘는다.
            # 여기서 next 가 끝나면 메인 세션이 next 를 다시 불러 다음 차례를 돌린다.
            task("continue_notice", PerformedBy.MAIN_SESSION_SHOW, Ref("plan_run.continue_notice"),
                 run_if=Ref("plan_run.stopped_at", {"value": "continue"}), reads=("find_plan", "run_nodes")),
            group("confirm", ChildRun.IN_ORDER,
                task("show_confirm", PerformedBy.MAIN_SESSION_TALK, Ref("plan_run.show_confirm"),
                     reads=("find_plan", "run_nodes")),
                task("ask_confirm", PerformedBy.MAIN_SESSION_ASK, Ref("plan_run.ask_confirm"),
                     reads=("find_plan", "run_nodes")),
                task("finish_confirm", PerformedBy.CODE, Ref("plan_run.finish_confirm"),
                     reads=("find_plan", "run_nodes", "show_confirm", "ask_confirm")),
                run_if=Ref("plan_run.stopped_at", {"value": "confirm"}), reads=("run_nodes",)),
            group("failed", ChildRun.IN_ORDER,
                task("ask_failed", PerformedBy.MAIN_SESSION_ASK, Ref("plan_run.ask_failed"),
                     reads=("find_plan", "run_nodes")),
                task("apply_failed", PerformedBy.CODE, Ref("plan_run.apply_failed"),
                     reads=("find_plan", "run_nodes", "ask_failed")),
                run_if=Ref("plan_run.stopped_at", {"value": "failed"}), reads=("run_nodes",)),
            for_each_item_in=Ref("plan_run.rounds"),
            run_if=Ref("plan_run.not_stopped", {"upto": "prompts"}),
            reads=("find_plan", "check_broken", "apply_rerun", "retry_prompts")),
        task("finish_plan", PerformedBy.CODE, Ref("plan_run.finish_plan"), reads=("find_plan",)),
        task("wip_notice", PerformedBy.MAIN_SESSION_SHOW, Ref("plan_run.wip_notice"),
             reads=("find_plan", "check_broken", "apply_rerun", "write_prompts", "retry_prompts"))),
)  # fmt: skip
