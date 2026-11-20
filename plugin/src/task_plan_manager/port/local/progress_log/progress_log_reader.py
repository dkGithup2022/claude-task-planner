"""진행 기록 읽기. Claude Code 상태 줄이 몇 초마다 부른다."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.progress.progress_event import ProgressEvent


class ProgressLogReader(ABC):
    @abstractmethod
    def latest_for_session(self, session_id: str) -> ProgressEvent | None:
        """이 작업 폴더의 모든 계획 기록 가운데, 이 세션이 쓴 가장 최근 한 줄. 없으면 None.
        계획마다 파일의 끝만 읽는다."""
