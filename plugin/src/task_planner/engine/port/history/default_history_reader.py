"""DefaultHistoryReader: history.jsonl 을 읽는다."""

from __future__ import annotations

from task_planner.common import files
from task_planner.engine.model.history.history_entry import HistoryEntry
from task_planner.engine.model.run_state.flow_run_state import FlowRunState
from task_planner.engine.port.history.history_file_converter import HistoryFileConverter
from task_planner.engine.port.history.history_reader import HistoryReader
from task_planner.engine.port.run_location import run_dir


class DefaultHistoryReader(HistoryReader):
    def read_history(self, state: FlowRunState) -> list[HistoryEntry]:
        converter = HistoryFileConverter()
        rows = files.read_jsonl(run_dir(state.session_id, state.run_id) / "history.jsonl")
        return [converter.to_data(r) for r in rows]
