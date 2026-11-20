import json

import pytest

from task_plan_manager.model.progress.closed_progress import ClosedProgress
from task_plan_manager.model.progress.feedback_progress import FeedbackProgress
from task_plan_manager.model.progress.planning_progress import PlanningProgress
from task_plan_manager.model.progress.progress_event import ProgressEvent
from task_plan_manager.model.progress.reinforce_phase import ReinforcePhase
from task_plan_manager.model.progress.reinforce_progress import ReinforceProgress
from task_plan_manager.model.progress.run_node import RunNode
from task_plan_manager.model.progress.run_phase import RunPhase
from task_plan_manager.model.progress.run_progress import RunProgress
from task_plan_manager.port.local.progress_log.default_progress_log_reader import DefaultProgressLogReader
from task_plan_manager.port.local.progress_log.default_progress_log_writer import DefaultProgressLogWriter


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    """진행 기록은 CLI 를 부른 작업 폴더의 .plan/<plan_id>/ 아래에 생긴다."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def event(at, detail, session_id="s1", plan_id=11):
    return ProgressEvent(at=at, session_id=session_id, plan_id=plan_id, detail=detail)


EVERY_KIND = (
    PlanningProgress(started_at="2026-11-20T04:16:15Z"),
    FeedbackProgress(editing_since=None),
    ReinforceProgress(ReinforcePhase.DRAFT, 3, 7, "하위 기획 작성", "2026-11-20T04:36:55Z"),
    RunProgress(
        RunPhase.NODES, 7, 10, (RunNode(51, "UI 문서 작성", "2026-11-20T05:04:22Z"), RunNode(52, "백엔드", None))
    ),
    ClosedProgress(),
)


@pytest.mark.parametrize("detail", EVERY_KIND)
def test_should_read_back_what_was_appended(detail):
    DefaultProgressLogWriter().append(event("2026-11-20T05:00:00Z", detail))
    assert DefaultProgressLogReader().latest_for_session("s1") == event("2026-11-20T05:00:00Z", detail)


def test_should_append_one_line_per_event_with_detail_kind(work_dir):
    writer = DefaultProgressLogWriter()
    writer.append(event("2026-11-20T04:16:15Z", EVERY_KIND[0]))
    writer.append(event("2026-11-20T04:17:34Z", EVERY_KIND[1]))
    lines = (work_dir / ".plan" / "11" / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["detail"]["kind"] for line in lines] == ["planning", "feedback"]


def test_should_pick_latest_line_of_this_session_across_plans():
    writer = DefaultProgressLogWriter()
    writer.append(event("2026-11-20T04:00:00Z", EVERY_KIND[0], plan_id=10))
    writer.append(event("2026-11-20T05:00:00Z", EVERY_KIND[1], plan_id=11))
    writer.append(event("2026-11-20T06:00:00Z", EVERY_KIND[2], plan_id=10, session_id="other"))
    latest = DefaultProgressLogReader().latest_for_session("s1")
    assert latest is not None and latest.plan_id == 11 and latest.detail == EVERY_KIND[1]


def test_should_return_none_when_this_session_wrote_nothing():
    reader = DefaultProgressLogReader()
    assert reader.latest_for_session("s1") is None
    DefaultProgressLogWriter().append(event("2026-11-20T04:00:00Z", EVERY_KIND[0], session_id="other"))
    assert reader.latest_for_session("s1") is None


def test_should_skip_a_half_written_last_line(work_dir):
    DefaultProgressLogWriter().append(event("2026-11-20T04:00:00Z", EVERY_KIND[0]))
    with (work_dir / ".plan" / "11" / "progress.jsonl").open("a", encoding="utf-8") as file:
        file.write('{"at": "2026-11-20T05:00:00Z", "session_id": "s1", "pla')  # 다른 프로세스가 쓰는 중
    latest = DefaultProgressLogReader().latest_for_session("s1")
    assert latest is not None and latest.at == "2026-11-20T04:00:00Z"


def test_should_keep_a_title_with_line_separator_as_one_line():
    titled = RunProgress(RunPhase.NODES, 0, 1, (RunNode(51, "UI\u2028문서", None),))
    DefaultProgressLogWriter().append(event("2026-11-20T05:00:00Z", titled))
    latest = DefaultProgressLogReader().latest_for_session("s1")
    assert latest is not None and latest.detail == titled


def test_should_ignore_folders_that_are_not_plans(work_dir):
    DefaultProgressLogWriter().append(event("2026-11-20T04:00:00Z", EVERY_KIND[0]))
    (work_dir / ".plan" / "notes").mkdir()
    (work_dir / ".plan" / "notes" / "progress.jsonl").write_text("{}\n", encoding="utf-8")
    latest = DefaultProgressLogReader().latest_for_session("s1")
    assert latest is not None and latest.at == "2026-11-20T04:00:00Z"


def test_should_report_with_now_and_this_session(work_dir, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s1")
    (work_dir / ".plan" / "11").mkdir(parents=True)  # 계획을 등록하면 계획 폴더가 먼저 생긴다
    DefaultProgressLogWriter().report(11, EVERY_KIND[0])
    latest = DefaultProgressLogReader().latest_for_session("s1")
    assert latest is not None and latest.plan_id == 11 and latest.detail == EVERY_KIND[0]
    assert latest.at.endswith("Z")


def test_should_not_report_outside_claude_code(work_dir, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    DefaultProgressLogWriter().report(11, EVERY_KIND[0])
    assert not (work_dir / ".plan").exists()


def test_should_not_raise_when_report_cannot_write(work_dir, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s1")
    (work_dir / ".plan").write_text("계획 폴더 자리에 파일이 있음", encoding="utf-8")
    DefaultProgressLogWriter().report(11, EVERY_KIND[0])


def test_should_not_report_for_plan_not_in_this_work_folder(work_dir, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s1")
    DefaultProgressLogWriter().report(11, EVERY_KIND[0])  # 다른 폴더에서 등록한 계획: 빈 계획 폴더를 만들지 않는다
    assert not (work_dir / ".plan").exists()
