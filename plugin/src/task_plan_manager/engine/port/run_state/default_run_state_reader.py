"""DefaultRunStateReader: state.json 을 읽는다."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.engine.model.run_state.flow_run_state import FlowRunState
from task_plan_manager.engine.port.run_location import run_dir
from task_plan_manager.engine.port.run_state.run_state_file_converter import RunStateFileConverter
from task_plan_manager.engine.port.run_state.run_state_reader import RunStateReader


class DefaultRunStateReader(RunStateReader):
    def load_run(self, session_id: str, run_id: str) -> FlowRunState:
        return RunStateFileConverter().to_data(files.read_json(run_dir(session_id, run_id) / "state.json"))
