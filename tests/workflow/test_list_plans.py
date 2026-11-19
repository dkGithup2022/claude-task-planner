"""list_plans 를 CLI 로 돌린다: 작업 폴더의 계획 목록을 보이고 끝난다."""

import json

import pytest

from task_plan_manager.common import files
from task_plan_manager.entry.cli import main
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    return work


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


def _make_plan(title: str, status: PlanStatus) -> int:
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan(title, "# 명령", (1,))).plan_id
    writer.set_plan_status(plan_id, status)
    DefaultPlanFolderWriter().create_plan(plan_id, "# 명령")
    return plan_id


def test_should_show_plans_of_this_work_folder_and_finish(capsys):
    _make_plan("검색 기능 설계", PlanStatus.REVIEWING)
    _make_plan("로그인 개편", PlanStatus.APPROVED)

    shown = run(capsys, "start", "list_plans")
    assert shown["type"] == "finished"  # 마지막 보이기 글은 끝 지시에 실림
    assert shown["payload"]["text"] == (
        "명령 뒤에 계획 id 를 넣어 다시 불러 주세요. 예: /plan-go 7\n\n"
        "| id | 제목 | 상태 |\n|---|---|---|\n| 1 | 검색 기능 설계 | 검토 중 |\n| 2 | 로그인 개편 | 승인 |"
    )


def test_should_say_there_is_no_plan(capsys):
    shown = run(capsys, "start", "list_plans")
    assert shown["payload"]["text"].startswith("이 작업 폴더에 계획이 없습니다.")


def test_should_mark_folder_without_plan_in_store(capsys, mock_data_dir):
    _make_plan("검색 기능 설계", PlanStatus.REVIEWING)
    (mock_data_dir / "plans" / "1.json").unlink()
    shown = run(capsys, "start", "list_plans")
    assert "| 1 | (계획 저장소에 없음) |  |" in shown["payload"]["text"]
    assert files.read_json(mock_data_dir / "ids.json")["plan"] == 1
