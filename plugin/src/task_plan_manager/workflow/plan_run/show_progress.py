"""계획 실행의 진행 표시. 단계가 한 줄로 부르고, 무엇을 어떻게 기록할지는 여기서 정한다.
기록은 Claude Code 상태 줄이 읽어 그린다 (workflow/statusline/)."""

from __future__ import annotations

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_schedule import FINISHED
from task_plan_manager.model.progress.run_node import RunNode
from task_plan_manager.model.progress.run_phase import RunPhase
from task_plan_manager.model.progress.run_progress import RunProgress
from task_plan_manager.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter


def show_run_started(plan: Plan) -> None:
    """실행을 시작했다. 노드가 뜨기 전까지 첫 줄만 보인다."""
    _report_run(plan, RunPhase.NODES, ())


def show_writing_prompts(plan: Plan) -> None:
    """노드마다 작업 지시를 만드는 중."""
    _report_run(plan, RunPhase.PROMPTS, ())


def show_running_nodes(plan: Plan, started_at: dict[int, str]) -> None:
    """지금 실행 중인 노드들. started_at 은 노드 id → 띄운 시각. 비었으면 첫 줄만 보인다."""
    nodes = tuple(RunNode(node_id, plan.node(node_id).title, at) for node_id, at in started_at.items())
    _report_run(plan, RunPhase.NODES, nodes)


def show_waiting_answer(plan: Plan, phase: RunPhase, node: PlanNode) -> None:
    """확인 노드(CONFIRM)나 실패한 노드(FAILED)에 대해 사용자의 답을 기다린다."""
    _report_run(plan, phase, (RunNode(node.node_id, node.title, None),))


def show_finished(plan: Plan) -> None:
    """모든 노드가 끝났다."""
    _report_run(plan, RunPhase.FINISHED, ())


def _report_run(plan: Plan, phase: RunPhase, nodes: tuple[RunNode, ...]) -> None:
    done = sum(1 for node in plan.nodes if node.status in FINISHED)  # 완료·건너뜀
    DefaultProgressLogWriter().report(plan.plan_id, RunProgress(phase, done, len(plan.nodes), nodes))
