"""split_tree: 가짜 claude 로 한 층씩 나누기, 상한, HITL, 호출 기록을 본다."""

import re

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.split_tree import split_tree as split_module
from task_plan_manager.workflow.make_plan.split_plan.split_tree.prompt_split_child import SplitChild
from task_plan_manager.workflow.make_plan.split_plan.split_tree.prompt_split_output import SplitOutput
from task_plan_manager.workflow.make_plan.split_plan.split_tree.split_tree import split_tree

REQUEST_MD = "# 명령\n밤만쥬를 만든다.\n\n\n# 맥락\n- 에어프라이어\n\n\n# 산출물\n- 장보기 목록\n- 레시피"


def _child(name: str, kind: str = "작업") -> SplitChild:
    return SplitChild(name=name, kind=kind, scope=f"{name} 목적", source="일반적인 분해")


# 판단 대상 이름 → 가짜 판단 결과
DECISIONS = {
    "밤만쥬 만들기": SplitOutput(True, "산출물이 둘", [_child("재료 준비"), _child("굽기"), _child("맛 확인", "HITL")]),
    "재료 준비": SplitOutput(True, "앙금과 반죽이 다름", [_child("앙금 준비"), _child("반죽 만들기")]),
}


def _fake_caller(seen_inputs: list[str]):
    def caller(spec, user_input):
        seen_inputs.append(user_input)
        target = re.search(r"^- 이름: (.+)$", user_input, re.MULTILINE).group(1)
        output = DECISIONS.get(target, SplitOutput(False, "목표가 하나", []))
        return output, PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_split_layer_by_layer_and_give_local_ids_to_leaves(tmp_path):
    seen_inputs: list[str] = []
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PromptCallLog(tmp_path), _fake_caller(seen_inputs))

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
    split_tree("밤만쥬 만들기", REQUEST_MD, PromptCallLog(tmp_path), _fake_caller(seen_inputs))
    second_layer_input = next(text for text in seen_inputs if "- 이름: 재료 준비" in text)
    assert "  - 재료 준비: 재료 준비 목적 ◀ 판단 대상" in second_layer_input
    assert "  - [HITL] 맛 확인: 맛 확인 목적" in second_layer_input
    assert "## 명령\n밤만쥬를 만든다." in second_layer_input  # 명령서 목차를 한 단계 내림
    assert "# 검색 결과\n없음" in second_layer_input
    assert "- 밤만쥬 만들기: 명령서 전체. 산출물: 장보기 목록, 레시피\n" in second_layer_input  # 맨 위 작업은 한 줄


def test_should_stop_splitting_at_node_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(split_module, "MAX_NODES", 3)
    result = split_tree("밤만쥬 만들기", REQUEST_MD, PromptCallLog(tmp_path), _fake_caller([]))
    assert [leaf.name for leaf in result.tree.leaves()] == ["재료 준비", "굽기", "맛 확인"]
    assert result.warnings and "노드 상한 3개" in result.warnings[0]
