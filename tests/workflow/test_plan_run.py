"""plan_run 을 CLI 로 돌린다.
묶음 1 (find_plan, start_run, resume), 묶음 2 (prompts), 묶음 4 (rounds) 와 임시 끝 단계까지.
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


# ── 가짜 claude ─────────────────────────────────────────

FAKE_AGENT = r"""
import json, os, re, sys, time
user_input = sys.stdin.read()
log = os.environ["FAKE_AGENT_LOG"]
started = time.time()
if user_input.startswith("# 작업 지시"):  # 노드 실행
    result_path = re.search(r"^- 본문: (.+)$", user_input, re.M).group(1)
    node_id = result_path.split("/nodes/", 1)[1].split("/", 1)[0]
    time.sleep(float(os.environ.get("FAKE_NODE_SLEEP", "0")))
    failing = node_id in os.environ.get("FAKE_NODE_FAIL", "").split(",")
    if not failing:
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, "w", encoding="utf-8") as f:
            f.write("# 결과 " + node_id + "\n")
    answer = "status: blocked\n라이브러리 권한 없음" if failing else "status: done\n노드 " + node_id + " 마침"
    row = {"mode": "node", "node_id": int(node_id), "start": started, "end": time.time(), "input": user_input}
else:  # 작업 지시 만들기
    title = user_input.split("- 제목: ", 1)[1].split("\n", 1)[0]
    bad = os.environ.get("FAKE_AGENT_BAD", "")
    first = "조사를 마쳤습니다" if title in bad.split(",") else "## 전체 작업과 이 노드의 목표"
    answer = first + "\n" + title + " 작업 지시"
    row = {"mode": "prompt", "title": title, "input": user_input}
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"result": answer, "total_cost_usd": 0.4}, ensure_ascii=False))
"""


@pytest.fixture
def fake_agent(tmp_path, monkeypatch):
    """run_agent 대신 도는 가짜 claude. 작업 지시 만들기와 노드 실행을 함께 대신한다.
    FAKE_AGENT_BAD 에 적은 제목의 노드는 작업 지시 첫 줄을 틀리게,
    FAKE_NODE_FAIL 에 적은 id 의 노드는 막힘으로 답한다."""
    exe = tmp_path / "fake-agent"
    exe.write_text(f"#!{sys.executable}\n" + FAKE_AGENT)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", str(exe))
    monkeypatch.setenv("FAKE_AGENT_LOG", str(tmp_path / "agent.jsonl"))

    def bad(*titles: str) -> None:
        monkeypatch.setenv("FAKE_AGENT_BAD", ",".join(titles))

    return bad


def test_should_move_approved_plan_to_running(tmp_path, capsys):
    plan_id = _make_plan(PlanStatus.APPROVED)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    finished = run(capsys, "start", "plan_run")  # 마지막 보이기 단계의 글은 끝 지시에 실린다
    assert finished["type"] == "finished", finished
    assert finished["payload"]["text"].startswith(f'계획 {plan_id} "댓글 기능" 을 실행 중으로 두었습니다.')
    assert MockPlanApiReader().get_plan(plan_id).status is PlanStatus.RUNNING


def test_should_record_done_and_rerun_broken_node_when_resuming(tmp_path, capsys, fake_agent):
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

    finished = run(capsys, "done", "--answer", "모두 다시 실행")  # 다시 실행한 노드는 이어서 실행된다
    assert "모든 노드를 마쳤습니다" in finished["payload"]["text"]

    folder = DefaultPlanFolderReader()
    assert _node_status(plan_id, finished_id) is PlanNodeStatus.DONE
    finished_run = folder.read_run(plan_id, finished_id)
    assert finished_run is not None and finished_run.status is PlanNodeStatus.DONE and finished_run.finished_at
    assert [row["node_id"] for row in _agent_rows(tmp_path, "node")] == [broken_id]  # 결과가 있던 노드는 다시 돌지 않음
    rerun = folder.read_run(plan_id, broken_id)
    assert rerun is not None and rerun.round == 2 and rerun.status is PlanNodeStatus.DONE


def test_should_ask_once_and_rerun_all_broken_nodes(tmp_path, capsys, fake_agent):
    plan_id = _make_plan(PlanStatus.RUNNING)
    first_id = _add_running_node(plan_id, "API 구현", with_result=False)
    second_id = _add_running_node(plan_id, "화면 구현", with_result=False)
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    asked = run(capsys, "start", "plan_run")
    assert f'- 노드 {first_id} "API 구현"\n- 노드 {second_id} "화면 구현"' in asked["payload"]["question"]
    assert run(capsys, "done", "--answer", "모두 다시 실행")["type"] == "finished"  # 두 번째 질문 없음
    assert sorted(row["node_id"] for row in _agent_rows(tmp_path, "node")) == [first_id, second_id]


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


def _add_todo_node(plan_id: int, title: str, after: int | None = None) -> int:
    writer = MockPlanApiWriter()
    spec = f"### 하는 일\n{title} 작업을 한다\n\n### 산출물\n- 형태: 문서\n{title} 결과"
    node_id = writer.add_node(plan_id, NewNode(title, NodeKind.CODE, (2,), spec)).node_id
    if after is not None:
        writer.add_edge(plan_id, after, node_id)
    return node_id


def _agent_inputs(tmp_path) -> dict[str, str]:
    return {row["title"]: row["input"] for row in _agent_rows(tmp_path, "prompt")}


def _agent_rows(tmp_path, mode: str) -> list[dict]:
    rows = [json.loads(line) for line in (tmp_path / "agent.jsonl").read_text(encoding="utf-8").splitlines()]
    return [row for row in rows if row["mode"] == mode]


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
    assert len(_agent_rows(tmp_path, "prompt")) == (1 if answer == "멈추기" else 2)


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


# ── 묶음 4: 노드 실행 루프 ─────────────────────────────────────────


def _add_node(plan_id: int, title: str, kind: NodeKind, after: tuple[int, ...] = ()) -> int:
    """작업 지시가 미리 있는 노드 (작업 지시 만들기는 건너뛴다)."""
    writer = MockPlanApiWriter()
    personas = () if kind is NodeKind.HITL else (2,)
    node_id = writer.add_node(plan_id, NewNode(title, kind, personas, f"### 하는 일\n{title}")).node_id
    for previous_id in after:
        writer.add_edge(plan_id, previous_id, node_id)
    DefaultPlanFolderWriter().write_prompt(plan_id, node_id, f"## 전체 작업과 이 노드의 목표\n{title}")
    return node_id


def _simulation_plan() -> tuple[int, list[int]]:
    """시뮬레이션의 계획: 1 테이블(code) → 2 API(code), 3 화면 문서(document) → 4 확인 → 5 배포 문서(document)."""
    plan_id = _make_plan(PlanStatus.APPROVED)
    table = _add_node(plan_id, "테이블 설계", NodeKind.CODE)
    api = _add_node(plan_id, "API 구현", NodeKind.CODE, (table,))
    screen = _add_node(plan_id, "화면 설계", NodeKind.DOCUMENT, (table,))
    check = _add_node(plan_id, "스테이징 확인", NodeKind.HITL, (api, screen))
    deploy = _add_node(plan_id, "배포 문서", NodeKind.DOCUMENT, (check,))
    return plan_id, [table, api, screen, check, deploy]


def _statuses(plan_id: int) -> list[str]:
    return [node.status.value for node in MockPlanApiReader().get_plan(plan_id).nodes]


def test_should_run_simulation_with_retry_and_confirm(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id, (table, api, screen, check, deploy) = _simulation_plan()
    monkeypatch.setenv("FAKE_NODE_FAIL", str(screen))
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    asked = run(capsys, "start", "plan_run")  # 차례 1: 1 → 2·3, 3 이 막힘
    assert asked["type"] == "ask"
    assert asked["payload"]["question"].startswith(
        f'노드 {screen} "화면 설계" 이 끝나지 못했습니다.\n이유: 막힘\n요약: 라이브러리 권한 없음'
    )
    assert asked["payload"]["choices"] == ["다시 실행", "작업 지시를 고쳐 다시", "건너뛰기", "멈추기"]
    assert _statuses(plan_id) == ["done", "done", "failed", "todo", "todo"]

    monkeypatch.delenv("FAKE_NODE_FAIL")
    talk = run(capsys, "done", "--answer", "다시 실행")  # 차례 2: 3 을 2 회차로 → 4 확인
    assert talk["type"] == "talk"
    assert (
        talk["payload"]["opening"]
        == f'노드 {check} "스테이징 확인" 을 확인할 차례입니다. 확인하실 부분을 모아 보여 드리겠습니다.'
    )
    assert (
        f"/nodes/{api}/result.md" in talk["payload"]["goal"] and f"/nodes/{screen}/result.md" in talk["payload"]["goal"]
    )
    confirm = run(capsys, "done")
    assert confirm["payload"]["question"] == f'노드 {check} "스테이징 확인": 다음으로 넘어가도 될까요?'
    finished = run(capsys, "done", "--answer", "허가")  # 차례 3: 5 → 끝
    assert finished["type"] == "finished" and "모든 노드를 마쳤습니다" in finished["payload"]["text"]

    folder = DefaultPlanFolderReader()
    assert _statuses(plan_id) == ["done"] * 5
    screen_run = folder.read_run(plan_id, screen)
    assert screen_run is not None and screen_run.round == 2
    assert (tmp_path / "work" / ".plan" / str(plan_id) / "nodes" / str(screen) / "runs" / "1" / "prompt.md").exists()
    confirm_result = folder.read_output(plan_id, check)
    assert confirm_result is not None and confirm_result.result_path.read_text().startswith("# 확인: 스테이징 확인")
    deploy_run = folder.read_run(plan_id, deploy)
    assert deploy_run is not None and [(r.node_id, r.round) for r in deploy_run.read_inputs] == [(check, 1)]
    node_input = next(row["input"] for row in _agent_rows(tmp_path, "node") if row["node_id"] == api)
    assert node_input.startswith("# 작업 지시\n\n## 전체 작업과 이 노드의 목표\nAPI 구현")
    assert f'- 노드 {table} "테이블 설계": 완료, 1 회차' in node_input


def test_should_run_code_nodes_one_at_a_time_and_documents_together(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id = _make_plan(PlanStatus.APPROVED)
    codes = [_add_node(plan_id, f"코드 {order}", NodeKind.CODE) for order in range(2)]
    documents = [_add_node(plan_id, f"문서 {order}", NodeKind.DOCUMENT) for order in range(2)]
    monkeypatch.setenv("FAKE_NODE_SLEEP", "0.4")
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    assert run(capsys, "start", "plan_run")["type"] == "finished"
    rows = {row["node_id"]: row for row in _agent_rows(tmp_path, "node")}

    def overlap(first: int, second: int) -> bool:
        return rows[first]["start"] < rows[second]["end"] and rows[second]["start"] < rows[first]["end"]

    assert not overlap(codes[0], codes[1])
    assert overlap(documents[0], documents[1])


def test_should_skip_failed_node_and_followers(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id, (table, *_rest) = _simulation_plan()
    monkeypatch.setenv("FAKE_NODE_FAIL", str(table))
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    finished = run(capsys, "done", "--answer", "건너뛰기")
    assert finished["type"] == "finished" and "모든 노드를 마쳤습니다" in finished["payload"]["text"]
    assert _statuses(plan_id) == ["skipped"] * 5
    skipped_run = DefaultPlanFolderReader().read_run(plan_id, table)
    assert skipped_run is not None and skipped_run.skipped_reason == "사용자가 건너뜀"


def test_should_stop_and_ask_again_on_next_plan_run(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id, (_table, _api, screen, *_rest) = _simulation_plan()
    monkeypatch.setenv("FAKE_NODE_FAIL", str(screen))
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    finished = run(capsys, "done", "--answer", "멈추기")  # 남은 차례는 다시 묻지 않는다
    assert finished["type"] == "finished"
    assert finished["payload"]["text"] == (
        f'노드 {screen} "화면 설계" 에서 멈췄습니다. 이어 하려면 /task_plan_manager:plan-run {plan_id}'
    )
    assert _statuses(plan_id) == ["done", "done", "failed", "todo", "todo"]

    asked = run(capsys, "start", "plan_run")  # 다음 /plan-run 은 다시 묻는다. 이유는 run.json 에서
    assert asked["type"] == "ask"
    assert asked["payload"]["question"].startswith(
        f'노드 {screen} "화면 설계" 이 끝나지 못했습니다.\n이유: 막힘\n요약: 라이브러리 권한 없음'
    )


def test_should_show_reason_of_second_failure_in_same_round(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id, (_table, api, screen, *_rest) = _simulation_plan()
    monkeypatch.setenv("FAKE_NODE_FAIL", f"{api},{screen}")  # 같은 차례에 둘 다 막힘
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    first = run(capsys, "start", "plan_run")
    assert first["payload"]["question"].startswith(f'노드 {api} "API 구현" 이 끝나지 못했습니다.\n이유: 막힘')
    second = run(capsys, "done", "--answer", "건너뛰기")  # 다음 차례에 화면 설계를 묻는다
    assert second["type"] == "ask"
    assert second["payload"]["question"].startswith(
        f'노드 {screen} "화면 설계" 이 끝나지 못했습니다.\n이유: 막힘\n요약: 라이브러리 권한 없음'
    )


def test_should_stop_for_prompt_edit_and_keep_node_todo(tmp_path, capsys, fake_agent, monkeypatch):
    plan_id, (_table, _api, screen, *_rest) = _simulation_plan()
    monkeypatch.setenv("FAKE_NODE_FAIL", str(screen))
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    run(capsys, "start", "plan_run")
    finished = run(capsys, "done", "--answer", "작업 지시를 고쳐 다시")
    prompt_path = tmp_path / "work" / ".plan" / str(plan_id) / "nodes" / str(screen) / "prompt.md"
    assert finished["payload"]["text"] == (
        f"작업 지시 {prompt_path.resolve()} 를 고친 뒤 /task_plan_manager:plan-run {plan_id}"
    )
    assert _statuses(plan_id)[2] == "todo"
    screen_run = DefaultPlanFolderReader().read_run(plan_id, screen)
    assert screen_run is not None and screen_run.round == 2


def test_should_stop_when_confirm_is_denied(tmp_path, capsys, fake_agent):
    plan_id, (_table, _api, _screen, check, _deploy) = _simulation_plan()
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    assert run(capsys, "start", "plan_run")["type"] == "talk"
    run(capsys, "done")
    finished = run(capsys, "done", "--answer", "허가하지 않음")
    assert finished["payload"]["text"] == (
        f'노드 {check} "스테이징 확인" 을 허가하지 않아 멈췄습니다. 어떻게 할지 말씀해 주세요. '
        f"이어 하려면 /task_plan_manager:plan-run {plan_id}"
    )
    assert _statuses(plan_id) == ["done", "done", "done", "todo", "todo"]


def test_should_continue_in_next_round_after_cutoff(tmp_path, capsys, fake_agent, monkeypatch, package_home):
    from task_plan_manager.workflow.plan_run.rounds.run_nodes import run_until_question

    plan_id = _make_plan(PlanStatus.APPROVED)
    first = _add_node(plan_id, "문서 1", NodeKind.DOCUMENT)
    _add_node(plan_id, "문서 2", NodeKind.DOCUMENT, (first,))
    monkeypatch.setattr(run_until_question, "LAUNCH_CUTOFF_SECONDS", 0.1)
    monkeypatch.setenv("FAKE_NODE_SLEEP", "0.3")
    _session_with_command(tmp_path, f"/task_plan_manager:plan-run {plan_id}")

    # 첫 차례가 마감으로 "계속"이면 알림을 보이고 next 를 끝낸다. 다음 차례는 다음 next 에서 돈다
    shown = run(capsys, "start", "plan_run")
    assert shown["type"] == "show"
    assert shown["payload"]["text"] == (
        f"노드 1개를 마쳤습니다. 남은 노드 1개를 이어서 실행합니다.\n"
        f'- 노드 {first} "문서 1": .plan/{plan_id}/nodes/{first}/result.md'
    )
    assert _statuses(plan_id) == ["done", "todo"]
    assert run(capsys, "next")["type"] == "finished"
    assert _statuses(plan_id) == ["done", "done"]
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    by_item = json.loads(next(run_dir.glob("run_nodes_*/result.json")).read_text())["by_item"]
    assert by_item["1"]["stop_at"] == "continue" and [r["node_id"] for r in by_item["1"]["ran"]] == [first]
