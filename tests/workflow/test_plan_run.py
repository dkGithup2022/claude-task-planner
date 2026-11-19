"""plan_run 을 CLI 로 돌린다. 묶음 1 (find_plan, start_run, resume), 묶음 2 (prompts) 와 임시 끝 단계까지.
묶음마다 시험을 늘린다. 묶음 1 시험의 노드는 작업 지시를 미리 넣어 두어 작업 지시 만들기를 건너뛴다."""

import json
import stat
import sys

import pytest

from task_plan_manager.common.clock import utc_now
from task_plan_manager.entry.cli import hook, main
from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.local.plan_folder.plan_folder_location import result_file
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter

STARTED_AT = "2026-11-19T10:00:00Z"


@pytest.fixture(autouse=True)
def work_dir(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    return work


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


def _session_with_command(tmp_path, command: str) -> None:
    """세션 시작 훅을 흉내 내고, 사용자가 친 슬래시 명령을 대화 기록에 쓴다."""
    name, args = command.split(" ", 1)
    row = {
        "type": "user",
        "timestamp": utc_now().replace("Z", ".000Z"),
        "message": {"content": f"<command-name>{name}</command-name>\n<command-args>{args}</command-args>"},
    }
    path = tmp_path / "transcript.jsonl"
    path.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    hook("session-start", {"session_id": "s", "transcript_path": str(path)})


def _make_plan(status: PlanStatus, folder: bool = True) -> int:
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan("댓글 기능", "# 명령", (1,))).plan_id
    writer.set_plan_status(plan_id, status)
    if folder:
        DefaultPlanFolderWriter().create_plan(plan_id, "# 명령")
    return plan_id


def _add_running_node(plan_id: int, title: str, with_result: bool, with_run: bool = True) -> int:
    """실행 중으로 남은 노드. with_result 면 result.md 가 있다 (끝까지 했는데 기록만 못 함)."""
    writer = MockPlanApiWriter()
    node_id = writer.add_node(plan_id, NewNode(title, NodeKind.CODE, (1,), "### 하는 일")).node_id
    writer.update_node(plan_id, node_id, NodeChange(status=PlanNodeStatus.RUNNING))
    DefaultPlanFolderWriter().write_prompt(plan_id, node_id, "## 전체 작업과 이 노드의 목표\n미리 둔 작업 지시")
    if with_run:
        started = NodeRun(2, PlanNodeStatus.TODO).start(STARTED_AT, ())
        DefaultPlanFolderWriter().save_run(plan_id, node_id, started)
    if with_result:
        path = result_file(plan_id, node_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# 결과", encoding="utf-8")
    return node_id


def _node_status(plan_id: int, node_id: int) -> PlanNodeStatus:
    return MockPlanApiReader().get_plan(plan_id).node(node_id).status


def test_should_move_approved_plan_to_running(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.APPROVED)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    finished = run(capsys, "start", "plan_run")  # 마지막 보이기 단계의 글은 끝 지시에 실린다
    assert finished["type"] == "finished", finished
    assert finished["payload"]["text"].startswith(f'계획 {plan_id} "댓글 기능" 을 실행 중으로 두었습니다.')
    assert MockPlanApiReader().get_plan(plan_id).status is PlanStatus.RUNNING


def test_should_record_done_and_rerun_broken_node_when_resuming(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.RUNNING)
    finished_id = _add_running_node(plan_id, "테이블 설계", with_result=True)
    broken_id = _add_running_node(plan_id, "API 구현", with_result=False)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    asked = run(capsys, "start", "plan_run")
    assert asked["type"] == "ask"
    assert asked["payload"]["question"] == (
        f'아래 노드는 실행 중에 끊겼고 결과 파일이 없습니다.\n- 노드 {broken_id} "API 구현"\n다시 실행할까요?'
    )
    assert asked["payload"]["choices"] == ["모두 다시 실행", "멈추기"]
    assert run(capsys, "done", "--answer", "글쎄")["type"] == "ask"  # 선택지 밖의 답은 다시 묻는다

    shown = run(capsys, "done", "--answer", "모두 다시 실행")
    assert "을 실행 중으로 두었습니다" in shown["payload"]["text"]

    folder = DefaultPlanFolderReader()
    assert _node_status(plan_id, finished_id) is PlanNodeStatus.DONE
    finished_run = folder.read_run(plan_id, finished_id)
    assert finished_run is not None and finished_run.status is PlanNodeStatus.DONE and finished_run.finished_at
    assert _node_status(plan_id, broken_id) is PlanNodeStatus.TODO
    assert folder.read_run(plan_id, broken_id) == NodeRun(2, PlanNodeStatus.TODO)


def test_should_ask_once_and_rerun_all_broken_nodes(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.RUNNING)
    first_id = _add_running_node(plan_id, "API 구현", with_result=False)
    second_id = _add_running_node(plan_id, "화면 구현", with_result=False)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    asked = run(capsys, "start", "plan_run")
    assert f'- 노드 {first_id} "API 구현"\n- 노드 {second_id} "화면 구현"' in asked["payload"]["question"]
    assert run(capsys, "done", "--answer", "모두 다시 실행")["type"] == "finished"  # 두 번째 질문 없음
    assert _node_status(plan_id, first_id) is PlanNodeStatus.TODO
    assert _node_status(plan_id, second_id) is PlanNodeStatus.TODO


def test_should_stop_without_changing_broken_nodes(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.RUNNING)
    first_id = _add_running_node(plan_id, "API 구현", with_result=False)
    second_id = _add_running_node(plan_id, "화면 구현", with_result=False)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    finished = run(capsys, "done", "--answer", "멈추기")
    assert finished["type"] == "finished"
    assert finished["payload"]["text"] == (
        f"노드 {first_id}, {second_id} 에서 멈췄습니다. 이어 하려면 /task_plan_manager:plan-run {plan_id}"
    )
    assert _node_status(plan_id, first_id) is PlanNodeStatus.RUNNING
    assert _node_status(plan_id, second_id) is PlanNodeStatus.RUNNING
    assert DefaultPlanFolderReader().read_run(plan_id, first_id).status is PlanNodeStatus.RUNNING


def test_should_not_ask_when_resuming_without_broken_nodes(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.RUNNING)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")
    finished = run(capsys, "start", "plan_run")
    assert finished["type"] == "finished" and "을 실행 중으로 두었습니다" in finished["payload"]["text"]


def test_should_make_first_round_when_finished_node_has_no_run_record(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.RUNNING)
    node_id = _add_running_node(plan_id, "테이블 설계", with_result=True, with_run=False)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    assert run(capsys, "start", "plan_run")["type"] == "finished"
    recorded = DefaultPlanFolderReader().read_run(plan_id, node_id)
    assert recorded is not None and recorded.round == 1 and recorded.status is PlanNodeStatus.DONE


@pytest.mark.parametrize(
    ("status", "folder", "message"),
    [
        (PlanStatus.REVIEWING, True, "계획 1 은 검토 중 상태라 실행할 수 없습니다"),
        (PlanStatus.DONE, True, "계획 1 은 끝남 상태입니다"),
        (PlanStatus.APPROVED, False, "계획 1 의 계획 폴더가 이 작업 폴더에 없습니다"),
    ],
)
def test_should_fail_when_plan_is_not_runnable(tmp_path, capsys, status, folder, message):
    _make_plan(status, folder=folder)
    _session_with_command(tmp_path, "/task_plan_manager:plan-run 1")
    failed = run(capsys, "start", "plan_run")
    assert failed["type"] == "failed" and message in failed["payload"]["text"]
    assert MockPlanApiReader().get_plan(1).status is status


def test_should_fail_when_plan_is_missing(tmp_path, capsys):
    _session_with_command(tmp_path, "/task_plan_manager:plan-run 5")
    failed = run(capsys, "start", "plan_run")
    assert failed["type"] == "failed" and "계획 5 이 계획 저장소에 없습니다" in failed["payload"]["text"]


# ── 묶음 2: 작업 지시 만들기 ─────────────────────────────────────────

FAKE_AGENT = r"""
import json, os, sys
user_input = sys.stdin.read()
title = user_input.split("- 제목: ", 1)[1].split("\n", 1)[0]
log = os.environ["FAKE_AGENT_LOG"]
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"title": title, "input": user_input}, ensure_ascii=False) + "\n")
bad = os.environ.get("FAKE_AGENT_BAD", "")
first = "조사를 마쳤습니다" if title in bad.split(",") else "## 전체 작업과 이 노드의 목표"
print(json.dumps({"result": first + "\n" + title + " 작업 지시", "total_cost_usd": 0.4}, ensure_ascii=False))
"""


@pytest.fixture
def fake_agent(tmp_path, monkeypatch):
    """run_agent 대신 도는 가짜 claude. FAKE_AGENT_BAD 에 적은 제목의 노드는 첫 줄을 틀리게 답한다."""
    exe = tmp_path / "fake-agent"
    exe.write_text(f"#!{sys.executable}\n" + FAKE_AGENT)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", str(exe))
    monkeypatch.setenv("FAKE_AGENT_LOG", str(tmp_path / "agent.jsonl"))

    def bad(*titles: str) -> None:
        monkeypatch.setenv("FAKE_AGENT_BAD", ",".join(titles))

    return bad


def _add_todo_node(plan_id: int, title: str, after: int | None = None) -> int:
    writer = MockPlanApiWriter()
    spec = f"### 하는 일\n{title} 작업을 한다\n\n### 산출물\n- 형태: 문서\n{title} 결과"
    node_id = writer.add_node(plan_id, NewNode(title, NodeKind.CODE, (2,), spec)).node_id
    if after is not None:
        writer.add_edge(plan_id, after, node_id)
    return node_id


def _agent_inputs(tmp_path) -> dict[str, str]:
    rows = [json.loads(line) for line in (tmp_path / "agent.jsonl").read_text(encoding="utf-8").splitlines()]
    return {row["title"]: row["input"] for row in rows}


def test_should_write_prompts_with_spec_and_writing_rules(tmp_path, capsys, fake_agent):
    plan_id = _make_plan(PlanStatus.APPROVED)
    table_id = _add_todo_node(plan_id, "테이블 설계")
    api_id = _add_todo_node(plan_id, "API 구현", after=table_id)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    shown = run(capsys, "start", "plan_run")
    assert shown["type"] == "show"
    assert shown["payload"]["text"] == "노드 2개의 작업 지시를 만듭니다. 약 1분, $0.6~1.2 안팎"
    finished = run(capsys, "next")
    assert finished["type"] == "finished", finished
    assert "작업 지시 2개를 새로 만들었습니다" in finished["payload"]["text"]

    prompt = DefaultPlanFolderReader().read_prompt(plan_id, api_id)
    assert prompt is not None
    assert prompt.startswith("## 전체 작업과 이 노드의 목표\nAPI 구현 작업 지시\n\n## 이 노드의 산출물 스펙 (원문)\n")
    assert "### 하는 일\nAPI 구현 작업을 한다" in prompt and prompt.rstrip().endswith("원래 표기대로 둔다.")
    sent = _agent_inputs(tmp_path)["API 구현"]
    assert "# 앞 노드\n\n## 테이블 설계 (1)\n\n### 하는 일\n테이블 설계 작업을 한다" in sent
    assert "- 담당: be-developer" in sent and "be-developer: 백엔드 개발 역할" in sent
    assert "result.md" not in sent  # 앞 노드 결과의 위치는 넣지 않는다
    assert "(없음. 계획의 첫 노드)" in _agent_inputs(tmp_path)["테이블 설계"]


def test_should_keep_existing_prompt(tmp_path, capsys, fake_agent):
    plan_id = _make_plan(PlanStatus.APPROVED)
    kept_id = _add_todo_node(plan_id, "테이블 설계")
    DefaultPlanFolderWriter().write_prompt(plan_id, kept_id, "사람이 고친 작업 지시")
    _add_todo_node(plan_id, "API 구현", after=kept_id)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    assert run(capsys, "start", "plan_run")["payload"]["text"].startswith("노드 1개의 작업 지시를 만듭니다")
    run(capsys, "next")
    assert DefaultPlanFolderReader().read_prompt(plan_id, kept_id) == "사람이 고친 작업 지시"
    assert list(_agent_inputs(tmp_path)) == ["API 구현"]


def test_should_ask_once_and_retry_failed_prompts(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id = _make_plan(PlanStatus.APPROVED)
    table_id = _add_todo_node(plan_id, "테이블 설계")
    api_id = _add_todo_node(plan_id, "API 구현", after=table_id)
    fake_agent("API 구현")
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    asked = run(capsys, "next")
    assert asked["type"] == "ask"
    assert asked["payload"]["question"] == (
        "아래 노드는 작업 지시를 만들지 못했습니다.\n"
        f'- 노드 {api_id} "API 구현": 첫 줄이 정해진 제목이 아님\n다시 만들까요?'
    )
    assert asked["payload"]["choices"] == ["모두 다시 만들기", "멈추기"]
    assert DefaultPlanFolderReader().read_prompt(plan_id, api_id) is None

    fake_agent()  # 다시 만들면 맞게 답한다
    finished = run(capsys, "done", "--answer", "모두 다시 만들기")
    assert "작업 지시 2개를 새로 만들었습니다" in finished["payload"]["text"]
    assert DefaultPlanFolderReader().read_prompt(plan_id, api_id) is not None


@pytest.mark.parametrize("answer", ["멈추기", "모두 다시 만들기"])
def test_should_stop_when_prompt_still_missing(tmp_path, capsys, fake_agent, answer):
    plan_id = _make_plan(PlanStatus.APPROVED)
    api_id = _add_todo_node(plan_id, "API 구현")
    fake_agent("API 구현")  # 다시 만들어도 틀린다
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    run(capsys, "next")
    finished = run(capsys, "done", "--answer", answer)
    assert finished["payload"]["text"] == (
        f"노드 {api_id} 의 작업 지시를 만들지 못해 멈췄습니다. 이어 하려면 /task_plan_manager:plan-run {plan_id}"
    )
    calls = (tmp_path / "agent.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(calls) == (1 if answer == "멈추기" else 2)


def test_should_skip_prompts_when_stopped_at_broken_node(tmp_path, capsys, fake_agent, package_home):
    plan_id = _make_plan(PlanStatus.RUNNING)
    _add_running_node(plan_id, "API 구현", with_result=False)
    _add_todo_node(plan_id, "화면 구현")
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    finished = run(capsys, "done", "--answer", "멈추기")
    assert "에서 멈췄습니다" in finished["payload"]["text"]
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    assert not list(run_dir.glob("count_prompts_*"))
