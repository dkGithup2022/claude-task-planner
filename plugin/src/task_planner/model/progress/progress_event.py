"""진행 기록 한 줄 (.plan/<plan_id>/progress.jsonl). 그 순간 상태 줄에 보일 것 전체를 담는다.
화면에 나갈 글은 담지 않는다. 상태 줄이 단계(detail 의 종류)와 과정으로 정해진 글을 고른다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.progress.closed_progress import ClosedProgress
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.model.progress.planning_progress import PlanningProgress
from task_planner.model.progress.reinforce_progress import ReinforceProgress
from task_planner.model.progress.run_progress import RunProgress

ProgressDetail = PlanningProgress | FeedbackProgress | ReinforceProgress | RunProgress | ClosedProgress


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    at: str  # 기록한 시각 (ISO 8601 UTC)
    session_id: str  # 기록한 Claude Code 세션. 상태 줄은 자기 세션이 쓴 것만 그린다
    plan_id: int
    detail: ProgressDetail  # 단계마다 다른 내용. 종류가 상태 줄 첫 줄의 지금 단계를 정한다
