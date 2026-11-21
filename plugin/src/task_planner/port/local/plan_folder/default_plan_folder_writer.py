"""계획 폴더 쓰기 구현."""

from __future__ import annotations

import shutil
from dataclasses import replace

from task_planner.common import files
from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.shown_record import ShownRecord
from task_planner.port.local.plan_folder.dto.stop_mark import StopMark
from task_planner.port.local.plan_folder.node_run_file_converter import NodeRunFileConverter
from task_planner.port.local.plan_folder.plan_folder_exists_error import PlanFolderExistsError
from task_planner.port.local.plan_folder.plan_folder_location import (
    command_file,
    files_dir,
    prompt_file,
    result_file,
    round_dir,
    run_file,
    shown_file,
    stop_file,
)
from task_planner.port.local.plan_folder.plan_folder_writer import PlanFolderWriter
from task_planner.port.local.plan_folder.shown_record_file_converter import ShownRecordFileConverter
from task_planner.port.local.plan_folder.stop_mark_file_converter import StopMarkFileConverter


class DefaultPlanFolderWriter(PlanFolderWriter):
    def create_plan(self, plan_id: int, command_md: str) -> None:
        # .plan/<plan_id>/command.md 를 쓴다. 같은 명령서가 이미 있으면 그대로 두고, 다르면 덮어쓰지 않고 멈춘다
        command_path = command_file(plan_id)
        if not command_path.exists():
            files.write_text(command_path, command_md)
            return
        if command_path.read_text(encoding="utf-8") != command_md:
            raise PlanFolderExistsError(f"계획 {plan_id} 의 폴더에 다른 명령서가 이미 있습니다 ({command_path})")

    def write_prompt(self, plan_id: int, node_id: int, text: str) -> None:
        # 노드 폴더의 prompt.md 를 덮어쓴다. 노드 폴더는 여기서 처음 생긴다
        files.write_text(prompt_file(plan_id, node_id), text)

    def write_result(self, plan_id: int, node_id: int, text: str) -> None:
        # 노드 폴더의 result.md 를 덮어쓴다
        files.write_text(result_file(plan_id, node_id), text)

    def save_run(self, plan_id: int, node_id: int, run: NodeRun) -> None:
        # 노드 폴더의 run.json 을 덮어쓴다
        files.write_json(run_file(plan_id, node_id), NodeRunFileConverter().to_file(run))

    def archive_round(self, plan_id: int, node_id: int) -> int:
        # 다시 실행하기 전에, 지금 회차의 작업 지시·결과를 runs/<회차>/ 로 보관하고
        # run.json 의 회차를 하나 올려 저장한다. 올린 회차를 돌려준다
        current_run = _read_run_or_first(plan_id, node_id)
        _move_round_files_to_archive(plan_id, node_id, current_run.round)
        return self._save_next_round(plan_id, node_id, current_run)

    def save_shown(self, plan_id: int, record: ShownRecord) -> None:
        # 계획 폴더의 shown.json 을 덮어쓴다
        files.write_json(shown_file(plan_id), ShownRecordFileConverter().to_file(record))

    def save_stop(self, plan_id: int, mark: StopMark) -> None:
        # 계획 폴더의 stop.json 을 덮어쓴다
        files.write_json(stop_file(plan_id), StopMarkFileConverter().to_file(mark))

    def _save_next_round(self, plan_id: int, node_id: int, current_run: NodeRun) -> int:
        """회차를 올리고 상태를 todo 로 되돌려 저장한다. 다음 보관이 같은 폴더를 덮어쓰지 않게."""
        next_run = replace(current_run, round=current_run.round + 1, status=PlanNodeStatus.TODO)
        self.save_run(plan_id, node_id, next_run)
        return next_run.round


def _read_run_or_first(plan_id: int, node_id: int) -> NodeRun:
    """지금 실행 기록. 아직 없으면 1 회차로 본다."""
    run_json_path = run_file(plan_id, node_id)
    if not run_json_path.exists():
        return NodeRun(round=1, status=PlanNodeStatus.TODO)
    return NodeRunFileConverter().to_data(files.read_json(run_json_path))


def _move_round_files_to_archive(plan_id: int, node_id: int, round_no: int) -> None:
    """작업 지시는 복사하고(다시 실행에도 쓰므로), 결과와 결과 파일 폴더는 옮긴다."""
    archive_dir = round_dir(plan_id, node_id, round_no)
    archive_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_file(plan_id, node_id)
    if prompt_path.exists():
        shutil.copy2(prompt_path, archive_dir / prompt_path.name)
    for current_path in (result_file(plan_id, node_id), files_dir(plan_id, node_id)):
        if current_path.exists():
            shutil.move(current_path, archive_dir / current_path.name)
