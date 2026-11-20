"""HistoryReader: runs/<실행>/history.jsonl 읽기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.engine.model.history.history_entry import HistoryEntry
from task_plan_manager.engine.model.run_state.flow_run_state import FlowRunState


class HistoryReader(ABC):
    @abstractmethod
    def read_history(self, state: FlowRunState) -> list[HistoryEntry]:
        """history 를 다시 읽는다 (요약 등)."""
