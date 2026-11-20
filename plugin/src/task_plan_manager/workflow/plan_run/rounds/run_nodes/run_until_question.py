"""우리 루프: 실행할 수 있는 노드를 run_agent 로 실행하다가, 사용자에게 물을 것이 생기거나 30분 마감이 지나면 돌아간다.

빈 자리 채우기 (사용자, 2026-11-20): 하나가 끝날 때마다 노드 상태를 다시 읽고 빈 자리에 새 노드를 띄운다. 동시에 3개.
코드 노드는 같은 저장소를 고치므로 하나씩만 돈다 (사용자, 2026-11-20). 문서·조사 노드는 결과를 .plan/ 안에만 쓴다.
마감 (사용자, 2026-11-20 "마감 30분"): 시작하고 30분이 지나면 새 노드를 띄우지 않고,
돌던 노드가 끝나면 "계속"으로 돌아간다.
실패한 노드가 나와도 바로 멈추지 않고 상관없는 노드는 끝까지 돌린다 (기존 plan-run SKILL.md:46-47).
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any

from task_plan_manager.claude_utils.agent.run_agent import install_child_cleanup
from task_plan_manager.common.clock import utc_now
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_schedule import plan_progress, runnable_nodes, waiting_confirm_nodes
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.plan_run.rounds.run_nodes.node_outcome import NodeOutcome
from task_plan_manager.workflow.plan_run.rounds.run_nodes.node_steps import execute_node, finish_node, start_node
from task_plan_manager.workflow.plan_run.show_progress import show_running_nodes

PARALLEL = 3
LAUNCH_CUTOFF_SECONDS = 1800  # 이 뒤로는 새 노드를 띄우지 않는다


def run_until_question(plan_id: int, run_id: str) -> dict[str, Any]:
    """메인 세션이 물을 것 하나와 이번 차례에 돈 노드.
    stop_at: failed | confirm | continue | finished | blocked | stopped."""
    # 읽기: 이번 실행에서 사용자가 멈추기로 했으면 바로 돌아간다
    mark = DefaultPlanFolderReader().read_stop(plan_id)
    if mark is not None and mark.run_id == run_id:
        return _answer("stopped", None, [], {})
    install_child_cleanup()  # 명령이 끊기면 돌던 노드 실행도 끝낸다
    deadline = time.monotonic() + LAUNCH_CUTOFF_SECONDS
    running: dict[Future[NodeOutcome], PlanNode] = {}
    started_at: dict[int, str] = {}  # 실행 중인 노드 id → 띄운 시각 (상태 줄이 걸린 시간을 센다)
    ran: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        while True:
            plan = plan_api_reader().get_plan(plan_id)
            if time.monotonic() < deadline:
                for node in pick_nodes(plan, running.values()):
                    start_node(plan, node.node_id)  # 쓰기: 이 스레드에서만
                    started_at[node.node_id] = utc_now()
                    running[pool.submit(execute_node, plan, node)] = node
            if not running:
                break
            show_running_nodes(
                plan, started_at
            )  # 실행 중인 노드가 있을 때만 남긴다. 노드 사이에 빈 목록을 남기면 깜박인다
            finished = next(as_completed(running))
            started_at.pop(running.pop(finished).node_id)
            ran.append(finish_node(plan_id, finished.result()))  # 쓰기: 끝나는 대로 바로
    past_deadline = time.monotonic() >= deadline
    plan = plan_api_reader().get_plan(plan_id)
    show_running_nodes(plan, {})  # 이번 차례가 끝남: 끝난 노드가 계속 "실행 중" 으로 보이지 않게
    return _next_question(plan, ran, past_deadline)


def pick_nodes(plan: Plan, running: Iterable[PlanNode]) -> list[PlanNode]:
    """빈 자리만큼 고른다. 코드 노드는 도는 것이 없을 때 하나만."""
    running_nodes = list(running)
    running_ids = {node.node_id for node in running_nodes}
    code_busy = any(node.kind is NodeKind.CODE for node in running_nodes)
    picked: list[PlanNode] = []
    for node in runnable_nodes(plan, len(plan.nodes)):
        if len(running_nodes) + len(picked) >= PARALLEL:
            break
        if node.node_id in running_ids:
            continue
        if node.kind is NodeKind.CODE:
            if code_busy:
                continue
            code_busy = True
        picked.append(node)
    return picked


def _next_question(plan: Plan, ran: list[dict[str, Any]], past_deadline: bool) -> dict[str, Any]:
    """실패 > 확인 > 마감 지나 남은 일(계속) > 끝남 > 막힘."""
    failed = sorted(node.node_id for node in plan.nodes if node.status is PlanNodeStatus.FAILED)
    if failed:
        return _answer("failed", failed[0], ran, _failure_detail(plan.plan_id, failed[0]))
    confirm = waiting_confirm_nodes(plan)
    if confirm:
        return _answer("confirm", confirm[0].node_id, ran, {})
    progress = plan_progress(plan)
    if progress.finished:
        return _answer("finished", None, ran, {})
    if past_deadline and runnable_nodes(plan, 1):
        return _answer("continue", None, ran, {})
    return _answer("blocked", None, ran, {})


def _failure_detail(plan_id: int, node_id: int) -> dict[str, str]:
    """실패 처리 질문에 보일 이유와 요약. run.json 에서 읽는다.
    이유가 없으면(실패 이유를 남기기 전의 기록) 그렇게 적는다."""
    run = DefaultPlanFolderReader().read_run(plan_id, node_id)
    if run is None or run.failed_reason is None:
        return {"reason": "지난 실행에서 끝나지 못하고 남음", "summary": ""}
    return {"reason": run.failed_reason, "summary": run.failed_summary or ""}


def _answer(stop_at: str, node_id: int | None, ran: list[dict[str, Any]], detail: dict[str, str]) -> dict[str, Any]:
    return {"stop_at": stop_at, "node_id": node_id, "ran": ran, "detail": detail, "finished_at": utc_now()}
