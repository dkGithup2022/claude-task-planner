"""write_edges: 가짜 claude 의 간선을 정리하는 규칙(버리기, 순환 막기, 빠진 간선 더하기)을 본다."""

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_edges.prompt_edges_output import EdgesOutput
from task_plan_manager.workflow.make_plan.split_plan.write_edges.write_edges import write_edges
from task_plan_manager.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite

REQUEST_MD = "# 명령\n밤만쥬를 만든다."
OUTPUT_SPEC = "### 하는 일\n한다\n\n### 산출물\n- 형태: 표\n분량\n\n### 그 외 설명\n(없음)"


def _draft(local_id: str, *received: str) -> NodeDraft:
    prerequisites = tuple(Prerequisite(local_id=prior, what=f"{prior} 결과") for prior in received)
    return NodeDraft(
        local_id, f"작업 {local_id}", NodeKind.DOCUMENT, (1,), OUTPUT_SPEC, f"밤만쥬 / 작업 {local_id}", prerequisites
    )


# n1 → n2 → n3, n4 는 n1 의 산출물을 받는다고 적었지만 간선 프롬프트가 빠뜨림
DRAFTS = (_draft("n1"), _draft("n2", "n1"), _draft("n3", "n2"), _draft("n4", "n1"))


def _fake_caller(edges: list[EdgeDraft], seen_inputs: list[str]):
    def caller(spec, user_input):
        seen_inputs.append(user_input)
        return EdgesOutput(edges=edges), PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_drop_invalid_and_cycle_edges_and_add_missing_received_edges(tmp_path):
    proposed = [
        EdgeDraft("n1", "n2"),
        EdgeDraft("n2", "n3"),
        EdgeDraft("n3", "n1"),  # 순환
        EdgeDraft("n2", "n2"),  # 자기 자신
        EdgeDraft("n9", "n1"),  # 없는 작업
    ]
    result = write_edges(REQUEST_MD, DRAFTS, PromptCallLog(tmp_path), _fake_caller(proposed, []))

    assert result.edges == (EdgeDraft("n1", "n2"), EdgeDraft("n2", "n3"), EdgeDraft("n1", "n4"))
    assert any("n3 → n1: 넣으면 순환이 생겨" in warning for warning in result.warnings)
    assert any("n2 → n2: 자기 자신" in warning for warning in result.warnings)
    assert any("n9 → n1: 작업 목록에 없는" in warning for warning in result.warnings)
    assert len(list((tmp_path / "calls" / "edges").iterdir())) == 1


def test_should_keep_one_direction_when_both_directions_come(tmp_path):
    result = write_edges(
        REQUEST_MD, DRAFTS, PromptCallLog(tmp_path), _fake_caller([EdgeDraft("n2", "n4"), EdgeDraft("n4", "n2")], [])
    )
    assert EdgeDraft("n2", "n4") in result.edges and EdgeDraft("n4", "n2") not in result.edges


def test_should_list_all_nodes_with_received_outputs_in_one_input(tmp_path):
    seen_inputs: list[str] = []
    write_edges(REQUEST_MD, DRAFTS, PromptCallLog(tmp_path), _fake_caller([], seen_inputs))
    assert len(seen_inputs) == 1
    text = seen_inputs[0]
    n4_section = (
        "## n4\n- 경로: 밤만쥬 / 작업 n4\n- 종류: document\n"
        "- 받는 산출물:\n  - n1(작업 n1): n1 결과\n- 산출물:\n- 형태: 표\n분량"
    )
    assert n4_section in text
    assert "## n1\n- 경로: 밤만쥬 / 작업 n1\n- 종류: document\n- 받는 산출물:\n  (없음)" in text
