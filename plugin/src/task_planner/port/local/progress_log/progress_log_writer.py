"""진행 기록 쓰기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_planner.model.progress.progress_event import ProgressDetail, ProgressEvent


class ProgressLogWriter(ABC):
    @abstractmethod
    def append(self, event: ProgressEvent) -> None:
        """그 계획의 progress.jsonl 끝에 한 줄을 덧붙인다. 파일이 없으면 만든다."""

    @abstractmethod
    def report(self, plan_id: int, detail: ProgressDetail) -> None:
        """지금 시각과 지금 Claude Code 세션(CLAUDE_CODE_SESSION_ID)으로 한 줄을 남긴다.
        세션이 없거나, 이 작업 폴더에 그 계획 폴더가 없거나, 쓰지 못하면 남기지 않고 오류도 내지 않는다
        (보여 주기는 부가 기능이라 흐름을 멈추지 않는다)."""
