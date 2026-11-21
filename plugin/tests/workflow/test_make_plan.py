"""make_plan 을 CLI 로 돌린다. 한 단계씩 만들며 시험을 늘린다."""

import json
import stat
import sys

import pytest

from task_planner.common import files
from task_planner.common.clock import utc_now
from task_planner.entry.cli import hook, main
from task_planner.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_planner.workflow.make_plan.interview.interview_task import GOAL, OPENING

REQUEST_MD = "# 명령\n밤만쥬를 1인분 만든다.\n\n\n# 중요한 것\n(정하지 않음)\n\n\n# 산출물\n장보기 목록과 레시피"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    """계획 폴더(.plan/)는 CLI 를 부른 작업 폴더에 생긴다. 시험은 임시 폴더에서 부른다."""
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    return work


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


FAKE_CLAUDE = r"""
import json, re, sys

text = sys.stdin.read()
if text.startswith("# 실제 작업"):  # 관계있는 지식 고르기: 관계있는 것이 없다고 답한다
    output = {"ids": []}
elif "# 지금까지의 작업 트리" in text:  # split: 맨 위만 두 작업으로 나누고 나머지는 나누지 않는다
    target = re.search(r"^- 이름: (.+)$", text, re.MULTILINE).group(1)
    children = [
        {"name": "재료 준비", "kind": "작업", "scope": "재료를 고른다", "source": "일반적인 분해"},
        {"name": "레시피 작성", "kind": "작업", "scope": "레시피를 쓴다", "source": "일반적인 분해"},
    ]
    root = target == "밤만쥬 1인분 만들기"
    output = {"split": root, "why": "산출물이 둘", "children": children if root else []}
elif "# 대상 작업" in text:  # spec: 레시피 작성은 재료 준비의 산출물을 받는다
    name = re.search(r"^# 대상 작업\n- 이름: (.+)$", text, re.MULTILINE).group(1)
    needs = [{"what": "재료 목록", "source": "재료 준비"}] if name == "레시피 작성" else []
    output = {"name": name, "does": name + " 을 한다", "needs": needs,
              "output": {"form": "표", "contents": "내용"}, "notes": "", "persona_ids": [1], "kind": "document"}
elif '"changed_nodes"' in text:  # 간선 다시 정하기: 1(재료 준비) → 2(레시피 작성)
    output = {"edges": [{"from_id": 1, "to_id": 2}]}
else:  # write_request
    output = {"title": "밤만쥬 1인분 만들기", "request": REQUEST_MD}
print(json.dumps({"structured_output": output, "total_cost_usd": 0.01}, ensure_ascii=False))
"""


def _fake_claude(tmp_path, monkeypatch):
    """claude -p 대신 입력 글의 머리로 어떤 프롬프트인지 알아보고 정해진 출력을 돌려준다."""
    exe = tmp_path / "fake-claude"
    exe.write_text(f"#!{sys.executable}\nREQUEST_MD = {REQUEST_MD!r}\n" + FAKE_CLAUDE)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLANNER_CLAUDE_BIN", str(exe))


def _done_until_finished(capsys) -> bool:
    """done 으로 대화를 끝내고 finished 까지 간다. 마지막 show_plan 의 글은 끝 지시에 실린다."""
    return run(capsys, "done")["type"] == "finished"


def _write_interview_transcript(transcript_path):
    """Claude Code 대화 기록 모양으로 인터뷰 두 줄을 쓴다. 시각은 지금 (interview 구간 안)."""
    now = utc_now().replace("Z", ".000Z")
    rows = [
        {"type": "user", "timestamp": now, "message": {"content": "밤만쥬 1인분 만들기"}},
        {"type": "assistant", "timestamp": now, "message": {"content": [{"type": "text", "text": "도구는?"}]}},
    ]
    transcript_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")


def test_should_interview_then_write_request_from_the_interview_dialogue(tmp_path, monkeypatch, capsys, package_home):
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})  # 세션 시작 훅 대신

    talk = run(capsys, "start", "make_plan")
    assert talk["type"] == "talk" and talk["payload"] == {"goal": GOAL, "opening": OPENING}
    _write_interview_transcript(transcript_path)

    assert _done_until_finished(capsys)

    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    interview = files.read_json(next(run_dir.glob("interview_*/result.json")))["by_item"]["-"]
    assert interview["transcript"] == str(transcript_path)
    written = files.read_json(next(run_dir.glob("write_request_*/result.json")))["by_item"]["-"]
    assert written == {"title": "밤만쥬 1인분 만들기", "request": REQUEST_MD}
    sent = files.read_json(next(run_dir.glob("write_request_*/calls/1/request.json")))["user"]
    assert sent == "user: 밤만쥬 1인분 만들기\nassistant: 도구는?"


def test_should_fail_write_request_when_transcript_is_missing(tmp_path, monkeypatch, capsys):
    _fake_claude(tmp_path, monkeypatch)
    run(capsys, "start", "make_plan")  # 세션 시작 훅이 돌지 않아 대화 기록 경로가 없다
    failed = run(capsys, "done")
    assert failed["type"] == "failed" and "대화 기록 경로가 없습니다" in failed["payload"]["text"]


def test_should_register_plan_with_first_persona_and_make_plan_folder(tmp_path, monkeypatch, capsys, work_dir):
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)
    assert _done_until_finished(capsys)

    plan = MockPlanApiReader().get_plan(1)
    # 상태는 뒤 단계(prepare_show)가 reviewing 으로 바꾸므로 여기서는 보지 않는다
    assert (plan.title, plan.request, plan.persona_ids) == ("밤만쥬 1인분 만들기", REQUEST_MD, (1,))
    assert (work_dir / ".plan" / "1" / "command.md").read_text(encoding="utf-8") == REQUEST_MD


def test_should_fail_register_plan_when_there_is_no_persona(tmp_path, monkeypatch, capsys, mock_data_dir):
    _fake_claude(tmp_path, monkeypatch)
    files.write_json(mock_data_dir / "personas.json", {"personas": []})
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)
    failed = run(capsys, "done")
    assert failed["type"] == "failed" and "페르소나 목록이 비어" in failed["payload"]["text"]


def test_should_split_plan_into_nodes_and_edges_in_one_step(tmp_path, monkeypatch, capsys, package_home):
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)
    assert _done_until_finished(capsys)

    plan = MockPlanApiReader().get_plan(1)
    assert [node.title for node in plan.nodes] == ["재료 준비", "레시피 작성"]
    assert plan.prerequisites(plan.nodes[1].node_id) == (plan.nodes[0].node_id,)

    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    split_folder = next(run_dir.glob("split_plan_*"))
    split_result = files.read_json(split_folder / "result.json")["by_item"]["-"]
    assert split_result == {"node_ids": {"n1": 1, "n2": 2}, "edge_count": 1, "warnings": []}
    calls = split_folder / "files" / "calls"
    assert [len(list((calls / group).iterdir())) for group in ("split", "spec", "edges")] == [3, 2, 1]


def test_should_move_plan_to_reviewing_and_leave_shown_record(tmp_path, monkeypatch, capsys, package_home, work_dir):
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)
    assert _done_until_finished(capsys)

    assert MockPlanApiReader().get_plan(1).status.value == "reviewing"
    shown = files.read_json(work_dir / ".plan" / "1" / "shown.json")
    assert shown["transcript"] == str(transcript_path) and shown["shown_at"].endswith("Z")
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    summary = files.read_json(next(run_dir.glob("prepare_show_*/result.json")))["by_item"]["-"]["summary"]
    assert summary.startswith('계획 1 "밤만쥬 1인분 만들기" 을 만들었습니다. 노드 2개, 간선 1개.')
    assert "| 2 | 레시피 작성 | document | 1 |" in summary


def test_should_show_summary_with_next_commands_and_finish(tmp_path, monkeypatch, capsys):
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)

    shown = run(capsys, "done")
    assert shown["type"] == "finished"
    assert shown["payload"]["skill"] == "task-planner:plan-feedback 1"  # 보인 뒤 고치기 대화 스킬
    text = shown["payload"]["text"]
    assert text.startswith('계획 1 "밤만쥬 1인분 만들기" 을 만들었습니다.')
    assert text.endswith("고칠 곳이 있으면 대화로 말해 주세요.\n확정은 /plan-go 1, 불허는 /plan-cancel 1")


def test_should_turn_on_statusline_and_show_planning_then_feedback(tmp_path, monkeypatch, capsys, work_dir):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s")
    _fake_claude(tmp_path, monkeypatch)
    transcript_path = tmp_path / "transcript.jsonl"
    hook("session-start", {"session_id": "s", "transcript_path": str(transcript_path)})
    run(capsys, "start", "make_plan")
    _write_interview_transcript(transcript_path)
    assert _done_until_finished(capsys)

    records = (work_dir / ".plan" / "1" / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["detail"]["kind"] for line in records] == ["planning", "feedback"]
    settings = files.read_json(work_dir / ".claude" / "settings.local.json")
    assert settings["statusLine"]["command"].endswith("/plugin/bin/task-planner statusline")
    assert settings["statusLine"]["refreshInterval"] == 5
