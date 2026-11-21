"""write_specs: 가짜 claude 로 정의서를 저장 전 노드로 바꾸는 규칙을 본다."""

import re

from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.model.persona.persona import Persona
from task_planner.model.plan.node_kind import NodeKind
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.task_tree.task_tree import TaskTree
from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind
from task_planner.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_need import SpecNeed
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_output import SpecOutput
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_product import SpecProduct
from task_planner.workflow.make_plan.split_plan.write_specs.write_specs import write_specs

REQUEST_MD = "# 명령\n밤만쥬를 만든다.\n\n\n# 산출물\n레시피"
PARTICIPANTS = (Persona(1, "dankim-persona", "사용자의 기본 작업 역할"),)


def _tree() -> TaskTree:
    """밤만쥬 → 배합 설계(→ 반죽 배합, 앙금 배합), 굽기, 맛 확인(HITL). 맨 아래 n1~n4."""

    def item(key, name, kind=WorkKind.TASK):
        parent = key.rsplit(".", 1)[0] if "." in key else None
        return WorkItem(key, name, f"{name} 목적", kind, key.count("."), parent)

    tree = TaskTree.start("밤만쥬", "명령서 전체")
    tree = tree.with_children(
        "0", (item("0.1", "배합 설계"), item("0.2", "굽기"), item("0.3", "맛 확인", WorkKind.HITL))
    )
    tree = tree.with_children("0.1", (item("0.1.1", "반죽 배합"), item("0.1.2", "앙금 배합")))
    return tree.with_local_ids()


SPECS = {
    "반죽 배합": SpecOutput(
        "반죽 배합",
        "반죽 분량을 정한다",
        [SpecNeed("요청", "명령서")],
        SpecProduct("표", "재료와 g"),
        "1인분",
        [1],
        "document",
    ),
    "앙금 배합": SpecOutput("앙금 배합", "앙금 분량을 정한다", [], SpecProduct("표", "앙금 g"), "", [9], "research"),
    "굽기": SpecOutput(
        "굽기",
        "굽는 조건을 정한다",
        [SpecNeed("반죽과 앙금 분량", "배합 설계")],
        SpecProduct("문서", "온도와 시간"),
        "",
        [1],
        "code",
    ),
    "맛 확인": SpecOutput(
        "맛 확인 단계", "", [SpecNeed("굽기 조건", "굽기")], SpecProduct("결정", "허가"), "", [1], "hitl"
    ),
}


def _fake_caller(seen_inputs):
    def caller(spec, user_input):
        seen_inputs.append(user_input)
        target = re.search(r"^# 대상 작업\n- 이름: (.+)$", user_input, re.MULTILINE).group(1)
        return SPECS[target], PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_turn_specs_into_node_drafts_with_prerequisites(tmp_path):
    seen_inputs = []
    result = write_specs(REQUEST_MD, _tree(), PARTICIPANTS, PromptCallLog(tmp_path), _fake_caller(seen_inputs))
    drafts = {draft.local_id: draft for draft in result.drafts}

    assert [draft.local_id for draft in result.drafts] == ["n1", "n2", "n3", "n4"]
    assert drafts["n1"].prerequisites == ()  # 출처가 명령서면 선행 작업이 아니다
    # 출처가 상위 작업(배합 설계)이면 그 아래 맨 아래 작업 전부
    assert drafts["n3"].prerequisites == (
        Prerequisite("n1", "반죽과 앙금 분량"),
        Prerequisite("n2", "반죽과 앙금 분량"),
    )
    assert drafts["n3"].kind is NodeKind.CODE and drafts["n3"].path == "밤만쥬 / 굽기"
    # 트리에서 HITL 이면 종류는 hitl, 담당은 없음
    assert drafts["n4"].kind is NodeKind.HITL and drafts["n4"].persona_ids == ()
    assert drafts["n4"].output_spec.startswith("### 하는 일\n맛 확인 목적\n")  # does 가 비면 트리의 목적
    # 참여 페르소나에 없는 id(9)는 첫 참여 페르소나로
    assert drafts["n2"].persona_ids == (1,)
    assert any("담당 [9]" in warning for warning in result.warnings)
    assert any('정의서 이름 "맛 확인 단계"' in warning for warning in result.warnings)
    assert len(list((tmp_path / "calls" / "spec").iterdir())) == 4


def test_should_mark_target_and_list_participants_with_ids(tmp_path):
    seen_inputs = []
    write_specs(REQUEST_MD, _tree(), PARTICIPANTS, PromptCallLog(tmp_path), _fake_caller(seen_inputs))
    oven_input = next(text for text in seen_inputs if "- 이름: 굽기" in text)
    assert "  - 굽기: 굽기 목적 ◀ 정의서 대상" in oven_input
    assert "# 참여 페르소나\n- 1 dankim-persona: 사용자의 기본 작업 역할" in oven_input
