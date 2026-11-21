"""계획 만들기의 진행 표시. 단계가 한 줄로 부르고, 무엇을 어떻게 기록할지는 여기서 정한다.
기록은 Claude Code 상태 줄이 읽어 그린다 (workflow/statusline/)."""

from __future__ import annotations

from task_planner.common.clock import utc_now
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.model.progress.planning_progress import PlanningProgress
from task_planner.port.local.claude_settings.default_claude_settings_writer import DefaultClaudeSettingsWriter
from task_planner.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter
from task_planner.workflow.make_plan.statusline_command import statusline_command

STATUSLINE_REFRESH_SECONDS = 5  # 상태 줄을 다시 그리는 간격 (사용자, 2026-11-20)


def show_planning_started(plan_id: int) -> None:
    """계획을 등록한 직후. 이 작업 폴더에 상태 줄을 켜고 "계획 세우는 중" 을 보인다."""
    DefaultClaudeSettingsWriter().ensure_statusline(statusline_command(), STATUSLINE_REFRESH_SECONDS)
    DefaultProgressLogWriter().report(plan_id, PlanningProgress(started_at=utc_now()))


def show_feedback_turn(plan_id: int) -> None:
    """계획을 보였다. 사용자가 고칠 곳을 말하거나 확정·취소할 차례."""
    DefaultProgressLogWriter().report(plan_id, FeedbackProgress(editing_since=None))
