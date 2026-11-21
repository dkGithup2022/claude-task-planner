"""split_tree: 가짜 claude 로 한 층씩 나누기, 상한, HITL, 호출 기록, 지식 찾기와 거르기를 본다."""

import re

from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.claude_utils.prompt.prompt_call_error import PromptCallError
from task_planner.claude_utils.search_utils.prompt_relevant_context_output import RelevantContextOutput
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.split_tree import relevant_plan_knowledge as knowledge_module
from task_planner.workflow.make_plan.split_plan.split_tree import split_tree as split_module
from task_planner.workflow.make_plan.split_plan.split_tree.prompt_split_child import SplitChild
from task_planner.workflow.make_plan.split_plan.split_tree.prompt_split_output import SplitOutput
from task_planner.workflow.make_plan.split_plan.split_tree.split_tree import split_tree

REQUEST_MD = "# 명령\n밤만쥬를 만든다.\n\n\n# 맥락\n- 에어프라이어\n\n\n# 산출물\n- 장보기 목록\n- 레시피"
PERSONA_IDS = (1,)


def _child(name: str, kind: str = "작업") -> SplitChild:
    return SplitChild(name=name, kind=kind, scope=f"{name} 목적", source="일반적인 분해")


# 판단 대상 이름 → 가짜 판단 결과
DECISIONS = {
    "밤만쥬 만들기": SplitOutput(True, "산출물이 둘", [_child("재료 준비"), _child("굽기"), _child("맛 확인", "HITL")]),
    "재료 준비": SplitOutput(True, "앙금과 반죽이 다름", [_child("앙금 준비"), _child("반죽 만들기")]),
}


def _fake_caller(seen_inputs: list[str], picked_ids: list[int] | None = None, picking_fails: bool = False):
    """나누기 호출은 DECISIONS 로 답하고 입력을 seen_inputs 에 모은다.
    관계있는 지식 고르기 호출은 picked_ids 를 돌려주거나 (없으면 빈 목록), picking_fails 면 실패한다."""

    def caller(spec, user_input):
        if spec.name == "relevant_context":
            record = PromptCallRecord({"user": user_input}, {"ok": not picking_fails})
            if picking_fails:
                raise PromptCallError("시간 초과", record)
            return RelevantContextOutput(ids=picked_ids or []), record
        seen_inputs.append(user_input)
        target = re.search(r"^- 이름: (.+)$", user_input, re.MULTILINE).group(1)
        output = DECISIONS.get(target, SplitOutput(False, "목표가 하나", []))
        return output, PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_split_layer_by_layer_and_give_local_ids_to_leaves(tmp_path):
    seen_inputs: list[str] = []
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), _fake_caller(seen_inputs))

    leaves = [(leaf.local_id, leaf.name, leaf.kind.value) for leaf in result.tree.leaves()]
    assert leaves == [
        ("n1", "앙금 준비", "작업"),
        ("n2", "반죽 만들기", "작업"),
        ("n3", "굽기", "작업"),
        ("n4", "맛 확인", "HITL"),
    ]
    # 판단은 맨 위 1번, 층 1 의 작업 2개(HITL 은 판단하지 않음), 층 2 의 작업 2개 = 5번
    assert len(seen_inputs) == 5
    assert len(list((tmp_path / "calls" / "split").iterdir())) == 5
    assert result.warnings == ()


def test_should_show_tree_with_mark_and_say_no_search_results(tmp_path):
    seen_inputs: list[str] = []
    split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), _fake_caller(seen_inputs))
    second_layer_input = next(text for text in seen_inputs if "- 이름: 재료 준비" in text)
    assert "  - 재료 준비: 재료 준비 목적 ◀ 판단 대상" in second_layer_input
    assert "  - [HITL] 맛 확인: 맛 확인 목적" in second_layer_input
    assert "## 명령\n밤만쥬를 만든다." in second_layer_input  # 명령서 목차를 한 단계 내림
    assert "# 검색 결과\n없음" in second_layer_input
    assert "- 밤만쥬 만들기: 명령서 전체. 산출물: 장보기 목록, 레시피\n" in second_layer_input  # 맨 위 작업은 한 줄


def test_should_stop_splitting_at_node_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(split_module, "MAX_NODES", 3)
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), _fake_caller([]))
    assert [leaf.name for leaf in result.tree.leaves()] == ["재료 준비", "굽기", "맛 확인"]
    assert result.warnings and "노드 상한 3개" in result.warnings[0]


def _second_layer_input(seen_inputs: list[str]) -> str:
    return next(text for text in seen_inputs if "- 이름: 재료 준비" in text)


def test_should_put_picked_knowledge_into_split_input(tmp_path):
    # mock 검색은 mock 지식 1, 2 를 돌려주고, 가짜 하이쿠는 그중 2 만 고른다
    seen_inputs: list[str] = []
    caller = _fake_caller(seen_inputs, [2])
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), caller)

    assert "# 검색 결과\n## 테이블 설계 (지식 2)\n배열은 별도 테이블로 둔다." in _second_layer_input(seen_inputs)
    assert "(지식 1)" not in _second_layer_input(seen_inputs)
    assert len(list((tmp_path / "calls" / "relevant_context").iterdir())) == 5  # 판단마다 한 번 고른다
    assert result.warnings == ()


def test_should_say_search_failed_and_keep_splitting(tmp_path, monkeypatch):
    class FailingReader:
        def search(self, query):
            raise MemoryApiError("POST /memories/search 에 연결하지 못함")

    monkeypatch.setattr(knowledge_module, "memory_api_reader", FailingReader)
    seen_inputs: list[str] = []
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), _fake_caller(seen_inputs))

    assert "# 검색 결과\n(검색 실패)" in _second_layer_input(seen_inputs)
    assert len(seen_inputs) == 5  # 판단은 그대로 다 한다
    assert "재료 준비: 지식 검색 실패 (POST /memories/search 에 연결하지 못함)" in result.warnings


def test_should_not_call_picking_when_search_finds_nothing(tmp_path, monkeypatch):
    class EmptyReader:
        def search(self, query):
            return ()

    monkeypatch.setattr(knowledge_module, "memory_api_reader", EmptyReader)
    seen_inputs: list[str] = []
    # 고르기를 부르면 실패해 경고가 생기도록 둔다. 부르지 않아야 경고가 없다
    caller = _fake_caller(seen_inputs, picking_fails=True)
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), caller)

    assert "# 검색 결과\n없음" in _second_layer_input(seen_inputs)
    assert not (tmp_path / "calls" / "relevant_context").exists()
    assert result.warnings == ()


def test_should_use_first_search_results_when_picking_fails(tmp_path):
    seen_inputs: list[str] = []
    caller = _fake_caller(seen_inputs, picking_fails=True)
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PERSONA_IDS, PromptCallLog(tmp_path), caller)

    second = _second_layer_input(seen_inputs)
    assert "## 테이블 설계 (지식 1)" in second and "## 테이블 설계 (지식 2)" in second
    assert "재료 준비: 관계있는 지식 고르기 실패, 검색 앞 5개를 씀 (시간 초과)" in result.warnings
    assert len(list((tmp_path / "calls" / "relevant_context").iterdir())) == 5  # 실패한 호출도 남긴다
