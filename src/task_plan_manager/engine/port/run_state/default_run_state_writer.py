"""DefaultRunStateWriter: state.json 을 쓴다."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.engine.model.run_state.flow_run_state import FlowRunState
from task_plan_manager.engine.port.run_location import run_dir
from task_plan_manager.engine.port.run_state.run_state_file_converter import RunStateFileConverter
from task_plan_manager.engine.port.run_state.run_state_writer import RunStateWriter


class DefaultRunStateWriter(RunStateWriter):
    def save_run(self, state: FlowRunState) -> None:
        files.write_json(run_dir(state.session_id, state.run_id) / "state.json", RunStateFileConverter().to_file(state))
