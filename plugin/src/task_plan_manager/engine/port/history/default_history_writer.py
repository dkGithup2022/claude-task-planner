"""DefaultHistoryWriter: history.jsonl 에 한 줄 덧붙인다."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.engine.model.history.history_entry import HistoryEntry
from task_plan_manager.engine.model.run_state.flow_run_state import FlowRunState
from task_plan_manager.engine.port.history.history_file_converter import HistoryFileConverter
from task_plan_manager.engine.port.history.history_writer import HistoryWriter
from task_plan_manager.engine.port.run_location import run_dir


class DefaultHistoryWriter(HistoryWriter):
    def append_history(self, state: FlowRunState, entry: HistoryEntry) -> None:
        files.append_jsonl(
            run_dir(state.session_id, state.run_id) / "history.jsonl", HistoryFileConverter().to_file(entry)
        )
