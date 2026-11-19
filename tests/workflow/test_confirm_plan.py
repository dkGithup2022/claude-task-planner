"""plan_go / plan_cancel 을 CLI 로 돌린다. 한 단계씩 만들며 시험을 늘린다."""

import json
import stat
import sys
from pathlib import Path

import pytest

from task_plan_manager.common import files
from task_plan_manager.common.clock import utc_now
from task_plan_manager.entry.cli import hook, main
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.model.plan.shown_record import ShownRecord
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter

SHOWN_AT = "2026-11-19T00:00:00Z"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    return work


@pytest.fixture(autouse=True)
def shown_transcript(tmp_path):
    """계획을 보여 준 대화의 기록 파일. 보여 준 뒤 사용자가 피드백 한 줄을 했다."""
    path = tmp_path / "shown.jsonl"
    rows = [
        {"type": "user", "timestamp": "2026-11-18T23:00:00.000Z", "message": {"content": "보여 주기 전 말"}},
        {
            "type": "assistant",
            "timestamp": "2026-11-19T00:00:01.000Z",
            "message": {"content": [{"type": "text", "text": "계획을 보였습니다"}]},
        },
        {"type": "user", "timestamp": "2026-11-19T00:01:00.000Z", "message": {"content": "테스트는 따로 노드로 빼줘"}},
    ]
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    return path


FAKE_CLAUDE = r"""
import json, os, sys
sys.stdin.read()
print(os.environ["FAKE_CLAUDE_OUTPUT"])
"""


@pytest.fixture(autouse=True)
def fake_claude(tmp_path, monkeypatch):
    """claude -p 대신 FAKE_CLAUDE_OUTPUT 환경 변수의 출력을 돌려준다. 기본은 후보 없음."""
    exe = tmp_path / "fake-claude"
    exe.write_text(f"#!{sys.executable}\n" + FAKE_CLAUDE)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", str(exe))

    def answer(candidates):
        output = {"structured_output": {"candidates": candidates}, "total_cost_usd": 0.01}
        monkeypatch.setenv("FAKE_CLAUDE_OUTPUT", json.dumps(output, ensure_ascii=False))

    answer([])
    return answer


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


def _run_to_end(capsys, flow: str) -> str:
    """흐름을 시작해 끝까지 가고, 끝 지시에 실린 알림 글을 돌려준다."""
    finished = run(capsys, "start", flow)
    assert finished["type"] == "finished", finished
    return str(finished["payload"]["text"])


def _make_plan(title: str, status: PlanStatus = PlanStatus.REVIEWING, shown: bool = True) -> int:
    """계획 저장소에 계획을 만들고, 이 작업 폴더에 계획 폴더와 (shown 이면) 보여 준 기록을 남긴다."""
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan(title, "# 명령", (1,))).plan_id
    writer.set_plan_status(plan_id, status)
    DefaultPlanFolderWriter().create_plan(plan_id, "# 명령")
    if shown:
        transcript = str(Path.cwd().parent / "shown.jsonl")  # shown_transcript 픽스처가 쓴 파일
        DefaultPlanFolderWriter().save_shown(plan_id, ShownRecord(SHOWN_AT, transcript))
    return plan_id


def _session_with_commands(tmp_path, *commands: str) -> None:
    """세션 시작 훅을 흉내 내고, 사용자가 친 슬래시 명령들을 대화 기록에 쓴다."""
    transcript_path = tmp_path / "transcript.jsonl"
    rows = [
        {
            "type": "user",
            "timestamp": utc_now().replace("Z", ".000Z"),
            "message": {"content": f"<command-name>{name}</command-name>\n<command-args>{args}</command-args>"},
        }
        for name, args in (command.split(" ", 1) for command in commands)
    ]
    transcript_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})


def _find_plan_result(package_home) -> dict:
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    return files.read_json(next(run_dir.glob("find_plan_*/result.json")))["by_item"]["-"]


def test_should_read_plan_id_from_last_command_and_keep_shown_record(tmp_path, capsys, package_home):
    _make_plan("검색 기능 설계")
    _make_plan("로그인 개편")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1", "/task_plan_manager:plan-go 2")

    _run_to_end(capsys, "plan_go")
    assert _find_plan_result(package_home) == {
        "plan_id": 2,
        "title": "로그인 개편",
        "persona_ids": [1],
        "shown_at": SHOWN_AT,
        "transcript": str(tmp_path / "shown.jsonl"),
    }


def test_should_read_plan_cancel_command_too(tmp_path, capsys, package_home):
    _make_plan("검색 기능 설계")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-cancel 1")
    _run_to_end(capsys, "plan_cancel")
    assert _find_plan_result(package_home)["plan_id"] == 1


@pytest.mark.parametrize(
    ("setup", "commands", "message"),
    [
        (lambda: None, ("/task_plan_manager:run make_plan",), "명령에서 계획 id 를 찾지 못했습니다"),
        (lambda: None, ("/task_plan_manager:plan-go 5",), "계획 5 이 계획 저장소에 없습니다"),
        (
            lambda: _make_plan("계획", PlanStatus.APPROVED),
            ("/task_plan_manager:plan-go 1",),
            "승인 상태라 확정할 수 없습니다",
        ),
        (lambda: _make_plan("계획", shown=False), ("/task_plan_manager:plan-go 1",), "보여 준 기록이 없습니다"),
    ],
)
def test_should_fail_with_reason(tmp_path, capsys, setup, commands, message):
    setup()
    _session_with_commands(tmp_path, *commands)
    failed = run(capsys, "start", "plan_go")
    assert failed["type"] == "failed" and message in failed["payload"]["text"]


def test_should_fail_when_session_has_no_transcript(capsys):
    _make_plan("계획")
    failed = run(capsys, "start", "plan_go")
    assert failed["type"] == "failed" and "대화 기록 경로가 없어" in failed["payload"]["text"]


def _add_cycle(plan_id: int) -> None:
    writer = MockPlanApiWriter()
    first = writer.add_node(plan_id, NewNode("앞", NodeKind.DOCUMENT, (1,), "### 하는 일"))
    second = writer.add_node(plan_id, NewNode("뒤", NodeKind.DOCUMENT, (1,), "### 하는 일"))
    writer.add_edge(plan_id, first.node_id, second.node_id)
    writer.add_edge(plan_id, second.node_id, first.node_id)


def test_should_stop_approval_when_plan_has_cycle(tmp_path, capsys):
    _add_cycle(_make_plan("계획"))
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1")
    failed = run(capsys, "start", "plan_go")
    assert failed["type"] == "failed"
    assert (
        "계획 1 의 노드와 간선에 문제가 있어 확정하지 않았습니다.\n- 순환: 1 앞 → 2 뒤 → 1 앞"
        in failed["payload"]["text"]
    )


def test_should_not_check_edges_when_rejecting(tmp_path, capsys, package_home):
    _add_cycle(_make_plan("계획"))
    _session_with_commands(tmp_path, "/task_plan_manager:plan-cancel 1")
    _run_to_end(capsys, "plan_cancel")
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    assert not list(run_dir.glob("check_edges_*"))


def _extract_result(package_home) -> dict:
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    return files.read_json(next(run_dir.glob("extract_knowledge_*/result.json")))["by_item"]["-"]


def _sent_input(package_home) -> str:
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    return files.read_json(next(run_dir.glob("extract_knowledge_*/calls/1/request.json")))["user"]


def test_should_send_plan_nodes_and_feedback_after_shown_time(tmp_path, capsys, package_home):
    plan_id = _make_plan("할 일 CLI")
    MockPlanApiWriter().add_node(plan_id, NewNode("테스트 작성", NodeKind.CODE, (1,), "### 하는 일"))
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1")
    _run_to_end(capsys, "plan_go")

    sent = _sent_input(package_home)
    expected = (
        "# 계획\n제목: 할 일 CLI\n- 1 테스트 작성\n\n"
        "# 대화\nassistant: 계획을 보였습니다\nuser: 테스트는 따로 노드로 빼줘"
    )
    assert sent == expected
    assert _extract_result(package_home) == {"candidates": [], "warnings": []}


def test_should_drop_unusable_candidates_and_keep_first_16(tmp_path, capsys, package_home, fake_claude):
    good = {"type": "plan", "theme": "CLI 도구 개발", "content": "테스트는 따로 둔다", "quotes": ["따로 빼줘"]}
    fake_claude([{**good, "type": "attitude"}, {**good, "content": " "}] + [good] * 17)
    _make_plan("할 일 CLI")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1")
    run(capsys, "start", "plan_go")  # 후보 16 개마다 질문이 이어지므로 첫 질문에서 멈춘 채 결과만 본다

    result = _extract_result(package_home)
    assert len(result["candidates"]) == 16 and result["candidates"][0] == good
    assert result["warnings"] == [
        '종류가 "attitude" 인 후보를 버림: CLI 도구 개발',
        "작업 이름이나 내용이 빈 후보를 버림: CLI 도구 개발",
        "후보 17 개 가운데 앞의 16 개만 다룹니다",
    ]


def _plan_status(plan_id: int) -> str:
    from task_plan_manager.port.plan_api.mock_plan_api_reader import MockPlanApiReader

    return MockPlanApiReader().get_plan(plan_id).status.value


def _record_result(package_home) -> dict:
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    return files.read_json(next(run_dir.glob("record_decision_*/result.json")))["by_item"]["-"]


def test_should_approve_plan_on_plan_go(tmp_path, capsys, package_home):
    _make_plan("계획")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1")
    _run_to_end(capsys, "plan_go")
    assert _plan_status(1) == "approved"
    assert _record_result(package_home) == {"plan_id": 1, "status": "approved"}


def test_should_reject_plan_on_plan_cancel(tmp_path, capsys):
    _make_plan("계획")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-cancel 1")
    _run_to_end(capsys, "plan_cancel")
    assert _plan_status(1) == "rejected"


def test_should_refuse_decision_when_status_changed_after_find_plan():
    from task_plan_manager.workflow.confirm_plan.record_decision.decision_not_allowed_error import (
        DecisionNotAllowedError,
    )
    from task_plan_manager.workflow.confirm_plan.record_decision.record_decision_task import RecordDecisionTask

    plan_id = _make_plan("계획", PlanStatus.APPROVED)

    class FakeContext:
        def read(self, node_name):
            return {"plan_id": plan_id}

    with pytest.raises(DecisionNotAllowedError, match="승인 상태라 다시 확정할 수 없습니다"):
        RecordDecisionTask("approved").build_output(FakeContext(), None)


def test_should_notify_approval_with_next_command(tmp_path, capsys):
    _make_plan("검색 기능 설계")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-go 1")
    assert _run_to_end(capsys, "plan_go") == (
        '계획 1 "검색 기능 설계" 을 승인했습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0).\n실행은 /plan-run 1'
    )


def test_should_notify_rejection_as_end(tmp_path, capsys):
    _make_plan("검색 기능 설계")
    _session_with_commands(tmp_path, "/task_plan_manager:plan-cancel 1")
    assert _run_to_end(capsys, "plan_cancel") == (
        '계획 1 "검색 기능 설계" 을 불허했습니다. 이 계획은 끝났습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0).'
    )
