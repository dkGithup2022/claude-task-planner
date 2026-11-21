import json
from contextlib import chdir
from pathlib import Path

import pytest

from task_planner.model.progress.closed_progress import ClosedProgress
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.model.progress.progress_event import ProgressEvent
from task_planner.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter
from task_planner.workflow.statusline.draw_statusline import draw_statusline


@pytest.fixture(autouse=True)
def folders(tmp_path, monkeypatch):
    """작업 폴더와 사용자 설정 폴더(CLAUDE_CONFIG_DIR). 명령은 다른 폴더에서 불린다."""
    (tmp_path / "work").mkdir()
    (tmp_path / "user").mkdir()
    (tmp_path / "elsewhere").mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "user"))
    monkeypatch.chdir(tmp_path / "elsewhere")
    return tmp_path


def status_input(folders: Path, session_id: str = "s1") -> str:
    return json.dumps({"session_id": session_id, "workspace": {"current_dir": str(folders / "work")}})


def write_record(folders: Path, detail, session_id: str = "s1") -> None:
    """흐름은 작업 폴더에서 돌며 기록을 남긴다."""
    event = ProgressEvent(at="2026-11-20T05:00:00Z", session_id=session_id, plan_id=11, detail=detail)
    with chdir(folders / "work"):
        DefaultProgressLogWriter().append(event)


def set_user_statusline(folders: Path, command: str) -> None:
    (folders / "user" / "settings.json").write_text(json.dumps({"statusLine": {"command": command}}), encoding="utf-8")


def test_should_draw_this_sessions_record_from_the_work_folder(folders):
    write_record(folders, FeedbackProgress(editing_since=None))
    lines = draw_statusline(status_input(folders))
    assert lines[0] == "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › [계획 피드백] › 지식 강화 › 실행"


@pytest.mark.parametrize("stdin_text", ["", "not json", json.dumps({"workspace": {}})])
def test_should_draw_nothing_without_session(folders, stdin_text):
    write_record(folders, FeedbackProgress(editing_since=None))
    assert draw_statusline(stdin_text) == []


def test_should_draw_nothing_for_other_sessions_or_rejected_plan(folders):
    write_record(folders, FeedbackProgress(editing_since=None), session_id="other")
    assert draw_statusline(status_input(folders)) == []
    write_record(folders, ClosedProgress())
    assert draw_statusline(status_input(folders)) == []


def test_should_pass_the_same_input_to_user_statusline(folders):
    received = folders / "received.json"
    set_user_statusline(folders, f"cat > {received}; echo 원래 상태 줄의 글")
    lines = draw_statusline(status_input(folders))
    assert json.loads(received.read_text(encoding="utf-8"))["session_id"] == "s1"
    assert "원래 상태 줄의 글" not in lines


def test_should_not_call_itself_when_user_statusline_is_ours(folders):
    marker = folders / "called"
    set_user_statusline(folders, f"touch {marker}; echo /plugin/bin/task-planner statusline")
    draw_statusline(status_input(folders))
    assert not marker.exists()
