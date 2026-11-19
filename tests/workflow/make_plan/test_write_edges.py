"""write_edges: 저장 전 노드 전부를 간선 다시 정하기에 넘기고, 받은 간선을 local_id 로 되돌리는지 본다.
거르기 규칙 자체는 tests/workflow/relink_edges 에서 본다."""

import json

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_edges.write_edges import write_edges
from task_plan_manager.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite
from task_plan_manager.workflow.relink_edges.prompt_relink_edges_edge import RelinkEdgesEdge
from task_plan_manager.workflow.relink_edges.prompt_relink_edges_output import RelinkEdgesOutput

OUTPUT_SPEC = "### 하는 일\n한다\n\n### 산출물\n- 형태: 표\n분량\n\n### 그 외 설명\n(없음)"


def _draft(local_id: str, *received: str) -> NodeDraft:
    prerequisites = tuple(Prerequisite(local_id=prior, what=f"{prior} 결과") for prior in received)
    return NodeDraft(
        local_id, f"작업 {local_id}", NodeKind.DOCUMENT, (1,), OUTPUT_SPEC, f"밤만쥬 / 작업 {local_id}", prerequisites
    )


# n2 는 n1, n3 은 n2 의 산출물을 받는다고 정의서에 적었다
DRAFTS = (_draft("n1"), _draft("n2", "n1"), _draft("n3", "n2"))


def _fake_caller(edges: list[tuple[int, int]], seen_inputs: list[str]):
    def caller(spec, user_input):
        seen_inputs.append(user_input)
        output = RelinkEdgesOutput([RelinkEdgesEdge(from_id, to_id) for from_id, to_id in edges])
        return output, PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_send_all_nodes_as_changed_with_received_outputs_as_previous_edges(tmp_path):
    seen_inputs: list[str] = []
    write_edges(DRAFTS, PromptCallLog(tmp_path), _fake_caller([], seen_inputs))
    sent = json.loads(seen_inputs[0])
    assert sent["change"] == "계획을 처음 만듦: 노드 3개"
    assert [(node["id"], node["title"]) for node in sent["changed_nodes"]] == [
        (1, "작업 n1"),
        (2, "작업 n2"),
        (3, "작업 n3"),
    ]
    assert sent["changed_nodes"][0]["output"] == {"form": "표", "contents": "분량"}
    assert sent["original_nodes"] == [] and sent["neighbor_nodes"] == []
    assert sent["previous_edges"] == [{"from": 1, "to": 2}, {"from": 2, "to": 3}]
    assert len(list((tmp_path / "calls" / "edges").iterdir())) == 1


def test_should_turn_numbers_back_to_local_ids_and_warn_with_local_ids(tmp_path):
    result = write_edges(DRAFTS, PromptCallLog(tmp_path), _fake_caller([(1, 2), (2, 3), (3, 1), (2, 2)], []))
    assert result.edges == (EdgeDraft("n1", "n2"), EdgeDraft("n2", "n3"))
    assert result.warnings == (
        "간선 프롬프트의 간선 n3 → n1: 넣으면 순환이 생겨 넣지 않음",
        "간선 프롬프트의 간선 n2 → n2: 자기 자신을 잇는 간선이라 버림",
    )


def test_should_not_call_prompt_for_single_node(tmp_path):
    seen_inputs: list[str] = []
    assert write_edges(DRAFTS[:1], PromptCallLog(tmp_path), _fake_caller([], seen_inputs)).edges == ()
    assert seen_inputs == []
