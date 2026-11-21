"""계획 확정의 진행 표시. 단계가 한 줄로 부르고, 무엇을 어떻게 기록할지는 여기서 정한다.
기록은 Claude Code 상태 줄이 읽어 그린다 (workflow/statusline/)."""

from __future__ import annotations

from task_planner.common.clock import utc_now
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.model.progress.closed_progress import ClosedProgress
from task_planner.model.progress.progress_event import ProgressDetail
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.model.progress.reinforce_progress import ReinforceProgress
from task_planner.model.progress.run_phase import RunPhase
from task_planner.model.progress.run_progress import RunProgress
from task_planner.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter

# 도구가 일하는 과정. 시작 시각을 남겨 상태 줄이 걸린 시간을 센다. 나머지는 사용자 차례
WORKING_PHASES = frozenset({ReinforcePhase.EXTRACT, ReinforcePhase.DRAFT, ReinforcePhase.FINALIZE})


def show_knowledge_step(context: FlowContext, phase: ReinforcePhase) -> None:
    """지식 강화에서 지금 하는 일. 후보 번호·수·주제는 앞 결과에서 꺼낸다. 후보를 뽑는 중이면 후보 정보가 없다.
    부르는 단계의 reads 에 find_plan 이, 후보를 다루는 단계면 extract_knowledge 도 있어야 한다."""
    plan_id = context.read("find_plan")["plan_id"]
    started_at = utc_now() if phase in WORKING_PHASES else None
    if phase is ReinforcePhase.EXTRACT:
        detail = ReinforceProgress(phase, None, None, None, started_at)
    else:
        total = len(context.read("extract_knowledge")["candidates"])
        theme = context.current_item()["theme"]
        detail = ReinforceProgress(phase, int(context.item_key or "1"), total, theme, started_at)
    DefaultProgressLogWriter().report(plan_id, detail)


def show_decision(plan_id: int, decision: PlanStatus, node_count: int) -> None:
    """승인이면 실행할 차례, 불허면 상태 줄을 닫는다."""
    detail: ProgressDetail = (
        RunProgress(RunPhase.READY, 0, node_count) if decision is PlanStatus.APPROVED else ClosedProgress()
    )
    DefaultProgressLogWriter().report(plan_id, detail)
