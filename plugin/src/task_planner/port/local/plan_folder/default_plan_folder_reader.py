"""계획 폴더 읽기 구현."""

from __future__ import annotations

from pathlib import Path

from task_planner.common import files
from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.plan.shown_record import ShownRecord
from task_planner.port.local.plan_folder.dto.node_output import NodeOutput
from task_planner.port.local.plan_folder.dto.result_target import ResultTarget
from task_planner.port.local.plan_folder.dto.stop_mark import StopMark
from task_planner.port.local.plan_folder.node_run_file_converter import NodeRunFileConverter
from task_planner.port.local.plan_folder.plan_folder_location import (
    command_file,
    files_dir,
    plan_root,
    prompt_file,
    result_file,
    run_file,
    shown_file,
    stop_file,
)
from task_planner.port.local.plan_folder.plan_folder_missing_error import PlanFolderMissingError
from task_planner.port.local.plan_folder.plan_folder_reader import PlanFolderReader
from task_planner.port.local.plan_folder.shown_record_file_converter import ShownRecordFileConverter
from task_planner.port.local.plan_folder.stop_mark_file_converter import StopMarkFileConverter


class DefaultPlanFolderReader(PlanFolderReader):
    def list_plan_ids(self) -> tuple[int, ...]:
        # .plan/ 아래 폴더 가운데 이름이 숫자인 것만 계획 id 로 본다
        root = plan_root()
        if not root.is_dir():
            return ()
        return tuple(sorted(int(folder.name) for folder in root.iterdir() if folder.is_dir() and folder.name.isdigit()))

    def read_command(self, plan_id: int) -> str:
        # .plan/<plan_id>/command.md 의 글을 그대로 돌려준다
        command_path = command_file(plan_id)
        if not command_path.exists():
            raise PlanFolderMissingError(f"계획 {plan_id} 의 명령서가 없습니다 ({command_path})")
        return command_path.read_text(encoding="utf-8")

    def read_prompt(self, plan_id: int, node_id: int) -> str | None:
        # 노드 폴더의 prompt.md 를 읽는다. 아직 쓰지 않았으면 None
        prompt_path = prompt_file(plan_id, node_id)
        return prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None

    def result_target(self, plan_id: int, node_id: int) -> ResultTarget:
        # 서브에이전트에게 넘길 결과 위치를 절대 경로로 계산만 한다
        return ResultTarget(
            result_path=result_file(plan_id, node_id).resolve(),
            files_dir=files_dir(plan_id, node_id).resolve(),
        )

    def read_output(self, plan_id: int, node_id: int) -> NodeOutput | None:
        # result.md 가 있으면 그 위치, files/ 아래 파일 목록, 실행 기록의 회차를 묶어 돌려준다
        result_path = result_file(plan_id, node_id)
        if not result_path.exists():
            return None
        run = self.read_run(plan_id, node_id)
        return NodeOutput(
            round=run.round if run else 1,
            result_path=result_path.resolve(),
            files=_list_result_files(files_dir(plan_id, node_id)),
        )

    def read_run(self, plan_id: int, node_id: int) -> NodeRun | None:
        # 노드 폴더의 run.json 을 읽는다. 아직 없으면 None
        run_json_path = run_file(plan_id, node_id)
        if not run_json_path.exists():
            return None
        return NodeRunFileConverter().to_data(files.read_json(run_json_path))

    def read_shown(self, plan_id: int) -> ShownRecord | None:
        # 계획 폴더의 shown.json 을 읽는다. 아직 없으면 None
        shown_path = shown_file(plan_id)
        if not shown_path.exists():
            return None
        return ShownRecordFileConverter().to_data(files.read_json(shown_path))

    def read_stop(self, plan_id: int) -> StopMark | None:
        # 계획 폴더의 stop.json 을 읽는다. 없으면 None
        stop_path = stop_file(plan_id)
        if not stop_path.exists():
            return None
        return StopMarkFileConverter().to_data(files.read_json(stop_path))


def _list_result_files(result_files_dir: Path) -> tuple[Path, ...]:
    """files/ 아래 하위 폴더까지 모든 파일의 절대 경로. 폴더가 없으면 빈 튜플."""
    if not result_files_dir.is_dir():
        return ()
    return tuple(sorted(path.resolve() for path in result_files_dir.rglob("*") if path.is_file()))
