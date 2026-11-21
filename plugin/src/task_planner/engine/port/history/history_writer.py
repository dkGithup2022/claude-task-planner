"""HistoryWriter: runs/<실행>/history.jsonl 에 한 줄 덧붙이기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_planner.engine.model.history.history_entry import HistoryEntry
from task_planner.engine.model.run_state.flow_run_state import FlowRunState


class HistoryWriter(ABC):
    @abstractmethod
    def append_history(self, state: FlowRunState, entry: HistoryEntry) -> None: ...
