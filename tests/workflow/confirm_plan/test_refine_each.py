"""refine_each (C): 후보마다 병합 / 새로 저장 / 넣지 않기를 고르고, 병합이면 대상을 쪽마다 넘겨 고른다.
mock 지식에 저장되는지 본다."""

import json
import stat
import sys

import pytest

from task_plan_manager.common import files
from task_plan_manager.entry.cli import hook, main
from task_plan_manager.model.memory.memory_kind import MemoryKind
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.model.plan.shown_record import ShownRecord
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory
from task_plan_manager.port.memory_api.mock_memory_api_writer import MockMemoryApiWriter
from task_plan_manager.port.memory_api.mock_memory_files import load_memories, save_memories
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_plan_manager.workflow.confirm_plan.refine_each.choose_target.merge_target import TARGET_PAGES
from task_plan_manager.workflow.confirm_plan.refine_each.choose_target.target_pages import has_next, page_of
from task_plan_manager.workflow.confirm_plan.refine_each.find_existing.find_existing_task import SEARCH_LIMIT

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


def test_should_save_new_merge_and_skip_by_choice(capsys, package_home):
    first = run(capsys, "start", "plan_go")
    assert first["type"] == "ask"
    question = first["payload"]["question"]
    head = '지식 후보 1/3: [계획] UI/UX 설계\n셋으로 나눈다\n근거: "셋으로 나눠줘"\n\n비슷한 지식 2개\n'
    assert question.startswith(head)
    assert " 1. #1 테이블 설계 — " in question and question.endswith("병합하시겠습니까?")
    assert first["payload"]["choices"] == ["병합", "새 지식으로 저장", "넣지 않기"]

    talk = run(capsys, "done", "--answer", "새 지식으로 저장")  # 고르기 쪽은 건너뜀
    assert talk["type"] == "talk" and talk["payload"]["opening"].startswith("[계획] UI/UX 설계 (새 지식)\n본문:\n")
    saved = run(capsys, "done")  # 대화 끝 → 최종 본문 → 저장 → 저장 결과를 보인다
    assert saved["type"] == "show"
    assert saved["payload"]["text"] == '지식 #3 "UI/UX 설계" 을 새로 저장했습니다.\n\nUI/UX 설계 확인한 본문'
    second = run(capsys, "next")
    assert second["type"] == "ask" and second["payload"]["question"].startswith("지식 후보 2/3")
    target = run(capsys, "done", "--answer", "병합")
    # 1 번 후보로 방금 저장한 #3 도 비슷한 지식으로 나온다 (mock 검색은 저장한 순서대로)
    assert target["payload"]["question"] == "어느 지식에 병합할까요? (1~3 / 3)"
    assert target["payload"]["choices"] == ["#1 테이블 설계", "#2 테이블 설계", "#3 UI/UX 설계"]
    talk = run(capsys, "done", "--answer", "#2 테이블 설계")
    assert talk["payload"]["opening"].startswith("[도메인] 테이블 설계 (#2 에 덧붙이기)\n덧붙일 내용:\n")
    saved = run(capsys, "done")
    assert saved["payload"]["text"].startswith('지식 #2 "테이블 설계" 에 덧붙였습니다.\n덧붙인 내용:\n\n')
    third = run(capsys, "next")
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


def test_should_turn_pages_and_merge_into_last_page_target(capsys):
    _add_memories(8)  # 기존 둘 + 여덟 = 10 개
    run(capsys, "start", "plan_go")
    page_1 = run(capsys, "done", "--answer", "병합")
    assert page_1["payload"]["question"] == "어느 지식에 병합할까요? (1~3 / 10)"
    assert page_1["payload"]["choices"] == ["#1 테이블 설계", "#2 테이블 설계", "#3 주제 3", "다음 3개 보기"]
    page_2 = run(capsys, "done", "--answer", "다음 3개 보기")
    assert page_2["payload"]["choices"] == ["#4 주제 4", "#5 주제 5", "#6 주제 6", "다음 3개 보기"]
    page_3 = run(capsys, "done", "--answer", "다음 3개 보기")
    assert page_3["payload"]["question"] == "어느 지식에 병합할까요? (7~10 / 10)"
    assert page_3["payload"]["choices"] == ["#7 주제 7", "#8 주제 8", "#9 주제 9", "#10 주제 10"]
    talk = run(capsys, "done", "--answer", "#10 주제 10")
    assert talk["payload"]["opening"].startswith("[계획] UI/UX 설계 (#10 에 덧붙이기)")
    run(capsys, "done")
    assert load_memories()[-1].body.endswith("UI/UX 설계 확인한 본문")


def test_should_skip_later_pages_after_choosing_on_first(capsys, package_home):
    _add_memories(8)
    run(capsys, "start", "plan_go")
    run(capsys, "done", "--answer", "병합")
    talk = run(capsys, "done", "--answer", "#3 주제 3")
    assert talk["type"] == "talk" and "(#3 에 덧붙이기)" in talk["payload"]["opening"]
    run_dir = next((package_home / "sessions" / "s" / "runs").iterdir())
    state = files.read_json(run_dir / "state.json")
    assert "choose_target_2" in json.dumps(state, ensure_ascii=False)  # 선언에는 있으나
    assert not list(run_dir.glob("choose_target_2_*/result.json"))  # 결과는 없다 (건너뜀)


def test_should_not_offer_merge_when_nothing_is_similar(capsys):
    save_memories(())
    first = run(capsys, "start", "plan_go")
    assert first["payload"]["choices"] == ["새 지식으로 저장", "넣지 않기"]
    assert "비슷한 지식이 없습니다." in first["payload"]["question"]


def test_should_offer_new_save_when_only_one_is_similar(capsys):
    save_memories(load_memories()[:1])
    run(capsys, "start", "plan_go")
    target = run(capsys, "done", "--answer", "병합")
    assert target["payload"]["choices"] == ["#1 테이블 설계", "새 지식으로 저장"]
    talk = run(capsys, "done", "--answer", "새 지식으로 저장")
    assert "(새 지식)" in talk["payload"]["opening"]


@pytest.mark.parametrize(("count", "pages"), [(10, [3, 3, 4]), (5, [3, 2]), (4, [4]), (1, [1])])
def test_should_split_targets_into_pages(count, pages):
    existing = [{"memory_id": number} for number in range(1, count + 1)]
    sizes, page = [], 1
    while True:
        sizes.append(len(page_of(existing, page)))
        if not has_next(existing, page):
            break
        page += 1
    assert sizes == pages


def _add_memories(count):
    writer = MockMemoryApiWriter()
    for number in range(3, 3 + count):
        writer.create(NewMemory(MemoryKind.PLAN, f"주제 {number}", f"본문 {number}", (1,), ()))


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


def test_should_fit_search_limit_into_declared_pages():
    # 기존 지식 찾기의 상한을 바꾸면 선언의 쪽 단계 수(셋)도 맞춰야 한다
    existing = [{"memory_id": number} for number in range(SEARCH_LIMIT)]
    assert has_next(existing, len(TARGET_PAGES) - 1) and not has_next(existing, len(TARGET_PAGES))
