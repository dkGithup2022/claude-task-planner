"""계획 고치기의 진행 표시. 기록은 Claude Code 상태 줄이 읽어 그린다 (workflow/statusline/)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from task_planner.common.clock import utc_now
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter


@contextmanager
def showing_edit(plan_id: int) -> Iterator[None]:
    """고치는 동안 "계획을 고치는 중" 을 보이고, 끝나면(성공이든 실패든) 피드백 차례로 되돌린다."""
    progress = DefaultProgressLogWriter()
    progress.report(plan_id, FeedbackProgress(editing_since=utc_now()))
    try:
        yield
    finally:
        progress.report(plan_id, FeedbackProgress(editing_since=None))
