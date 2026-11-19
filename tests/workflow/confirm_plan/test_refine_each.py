"""refine_each (C): 후보 세 개를 새로 저장 / 덧붙이기 / 넣지 않기로 다루고, mock 지식에 저장되는지 본다."""

import json
import stat
import sys

import pytest

from task_plan_manager.common import files
from task_plan_manager.entry.cli import hook, main
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.model.plan.shown_record import ShownRecord
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.memory_api.mock_memory_files import load_memories
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter

CANDIDATES = [
    {"type": "plan", "theme": "UI/UX 설계", "content": "셋으로 나눈다", "quotes": ["셋으로 나눠줘"]},
    {"type": "domain", "theme": "테이블 설계", "content": "FK 를 걸지 않는다", "quotes": ["fk 걸지 마"]},
    {"type": "domain", "theme": "SQL 조회", "content": "join 3번 이하", "quotes": ["조인 깊게 하지 마"]},
]

# 입력 글의 머리로 어떤 프롬프트인지 알아보고 답한다
FAKE_CLAUDE = r"""
import json, os, sys
text = sys.stdin.read()
if text.startswith("# 계획"):
    output = {"candidates": json.loads(os.environ["FAKE_CANDIDATES"])}
elif text.startswith("# 후보"):
    theme = text.split("작업 이름: ", 1)[1].split("\n", 1)[0]
    output = {"theme": theme, "body": theme + " 본문. 예 1. 예 2. 예 3."}
elif text.startswith("# 초안"):
    theme = text.split("작업 이름: ", 1)[1].split("\n", 1)[0]
    output = {"save": os.environ.get("FAKE_SAVE", "true") == "true", "theme": theme, "body": theme + " 확인한 본문"}
else:
    raise SystemExit("모르는 입력: " + text[:40])
print(json.dumps({"structured_output": output, "total_cost_usd": 0.01}, ensure_ascii=False))
"""


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    exe = tmp_path / "fake-claude"
    exe.write_text(f"#!{sys.executable}\n" + FAKE_CLAUDE)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", str(exe))
    monkeypatch.setenv("FAKE_CANDIDATES", json.dumps(CANDIDATES, ensure_ascii=False))
    # 계획을 보여 준 대화: 보여 준 뒤 피드백 세 줄
    shown = tmp_path / "shown.jsonl"
    feedback = ["셋으로 나눠줘", "fk 걸지 마", "조인 깊게 하지 마"]
    rows = [
        {"type": "user", "timestamp": f"2026-11-19T00:0{index}:00.000Z", "message": {"content": text}}
        for index, text in enumerate(feedback, start=1)
    ]
    shown.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    plan_id = MockPlanApiWriter().create_plan(NewPlan("계획", "# 명령", (1, 2))).plan_id
    MockPlanApiWriter().set_plan_status(plan_id, PlanStatus.REVIEWING)
    DefaultPlanFolderWriter().create_plan(plan_id, "# 명령")
    DefaultPlanFolderWriter().save_shown(plan_id, ShownRecord("2026-11-19T00:00:00Z", str(shown)))
    # 지금 대화: /plan-go 1
    session = tmp_path / "session.jsonl"
    command = "<command-name>/task_plan_manager:plan-go</command-name>\n<command-args>1</command-args>"
    session.write_text(json.dumps({"type": "user", "timestamp": "2026-11-19T01:00:00.000Z",
                                   "message": {"content": command}}), encoding="utf-8")  # fmt: skip
    hook("session-start", {"session_id": "s", "transcript_path": str(session)})


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


def test_should_save_new_append_and_skip_by_choice(capsys, package_home):
    first = run(capsys, "start", "plan_go")
    assert first["type"] == "ask"
    assert first["payload"]["question"].startswith(
        '지식 후보 1/3: [계획] UI/UX 설계\n셋으로 나눈다\n근거: "셋으로 나눠줘"'
    )
    assert "****** KNOWLEDGE SEARCHED 1 ********\n#1 테이블 설계" in first["payload"]["question"]
    assert first["payload"]["choices"] == [
        "새 지식으로 저장", "덧붙이기: #1 테이블 설계", "덧붙이기: #2 테이블 설계", "넣지 않기"]  # fmt: skip

    talk = run(capsys, "done", "--answer", "새 지식으로 저장")
    assert talk["type"] == "talk" and talk["payload"]["opening"].startswith("[계획] UI/UX 설계 (새 지식)\n본문:\n")
    second = run(capsys, "done")
    assert second["type"] == "ask" and second["payload"]["question"].startswith("지식 후보 2/3")
    talk = run(capsys, "done", "--answer", "덧붙이기: #2 테이블 설계")
    assert talk["payload"]["opening"].startswith("[도메인] 테이블 설계 (#2 에 덧붙이기)\n덧붙일 내용:\n")
    third = run(capsys, "done")
    assert third["payload"]["question"].startswith("지식 후보 3/3")
    notice = run(capsys, "done", "--answer", "넣지 않기")
    assert notice["type"] == "finished"  # 마지막 알림 글은 끝 지시에 실림
    assert "저장한 지식 2개 (새로 1, 덧붙이기 1)." in notice["payload"]["text"]

    memories = {memory.memory_id: memory for memory in load_memories()}
    assert memories[3].theme == "UI/UX 설계" and memories[3].body == "UI/UX 설계 확인한 본문"
    assert memories[3].kind.value == "plan" and memories[3].persona_ids == (1, 2)
    assert memories[2].body.endswith("\n\n****** KNOWLEDGE APPENDED 1 ********\n테이블 설계 확인한 본문")
    assert [source.quote for source in memories[2].sources][-1] == "fk 걸지 마"
    assert len(memories) == 3  # 세 번째 후보는 저장하지 않음

    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    written = files.read_json(next(run_dir.glob("write_knowledge_*/result.json")))["by_item"]
    assert sorted(written) == ["1", "2"]  # 넣지 않기를 고른 3 번은 본문을 쓰지 않았다
    sent = files.read_json(next(run_dir.glob("write_knowledge_*/calls/2/request.json")))["user"]
    assert "# 사용자 말과 바로 앞의 Claude 말\nuser: fk 걸지 마" in sent
    assert "# 덧붙일 기존 지식\n#2 테이블 설계\n배열은 별도 테이블로 둔다." in sent


def test_should_not_save_when_user_decided_not_to(capsys, monkeypatch):
    monkeypatch.setenv("FAKE_SAVE", "false")
    run(capsys, "start", "plan_go")
    run(capsys, "done", "--answer", "새 지식으로 저장")
    run(capsys, "done")  # 대화 끝 → finalize 가 저장하지 않기로
    assert len(load_memories()) == 2


def test_should_ask_again_for_answer_outside_choices(capsys):
    run(capsys, "start", "plan_go")
    again = run(capsys, "done", "--answer", "아무거나")
    assert again["type"] == "ask" and again["payload"]["question"].startswith("지식 후보 1/3")


def test_should_skip_refine_when_there_is_no_candidate(capsys, monkeypatch):
    monkeypatch.setenv("FAKE_CANDIDATES", "[]")
    notice = run(capsys, "start", "plan_go")
    assert notice["type"] == "finished" and "저장한 지식 0개" in notice["payload"]["text"]
