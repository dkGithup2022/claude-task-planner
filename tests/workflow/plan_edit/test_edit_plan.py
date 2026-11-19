"""plan show / plan edit: 묶음 동작을 미리 적용해 점검하고, 통과하면 mock 계획 저장소에 보낸다."""

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_plan_manager.workflow.plan_edit.edit_plan import edit_plan, show_plan

SPEC = "### 하는 일\n{}\n\n### 산출물\n- 형태: 문서\n\n### 그 외 설명\n(없음)"


def _plan_with_chain(status: PlanStatus = PlanStatus.REVIEWING) -> tuple[int, dict[str, int]]:
    """요구사항 → 화면 설계 → 화면 구현 세 노드를 잇는 계획. 제목 → node_id 를 돌려준다."""
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan("쇼핑몰 화면", "# 명령", (1,))).plan_id
    ids = {}
    for title, kind in [
        ("요구사항", NodeKind.DOCUMENT),
        ("화면 설계", NodeKind.DOCUMENT),
        ("화면 구현", NodeKind.CODE),
    ]:
        ids[title] = writer.add_node(plan_id, NewNode(title, kind, (1,), SPEC.format(title))).node_id
    writer.add_edge(plan_id, ids["요구사항"], ids["화면 설계"])
    writer.add_edge(plan_id, ids["화면 설계"], ids["화면 구현"])
    if status is not PlanStatus.DRAFTING:
        writer.set_plan_status(plan_id, PlanStatus.REVIEWING)
    if status not in (PlanStatus.DRAFTING, PlanStatus.REVIEWING):
        writer.set_plan_status(plan_id, status)
    return plan_id, ids


def _titled_edges(plan_id: int) -> set[tuple[str, str]]:
    plan = MockPlanApiReader().get_plan(plan_id)
    titles = {node.node_id: node.title for node in plan.nodes}
    return {(titles[edge.from_node_id], titles[edge.to_node_id]) for edge in plan.edges}


def _node(plan_id: int, title: str):
    return next(node for node in MockPlanApiReader().get_plan(plan_id).nodes if node.title == title)


def test_should_split_node_in_order_and_relink_before_and_after():
    plan_id, ids = _plan_with_chain()
    ops = {"ops": [{"op": "split", "node_id": ids["화면 설계"], "order": "serial", "into": [
        {"title": "와이어프레임 설계", "scope": "화면별 배치와 이동 흐름을 정한다."},
        {"title": "디자인 테마 설계", "scope": "색, 글꼴, 간격을 정한다.", "note": "기존 서비스 색을 그대로 쓴다."},
    ]}]}  # fmt: skip

    result = edit_plan(plan_id, ops)

    assert result["ok"] is True and result["problems"] == []
    assert _titled_edges(plan_id) == {
        ("요구사항", "와이어프레임 설계"), ("와이어프레임 설계", "디자인 테마 설계"), ("디자인 테마 설계", "화면 구현"),
    }  # fmt: skip
    theme = _node(plan_id, "디자인 테마 설계")
    assert theme.kind is NodeKind.DOCUMENT and theme.persona_ids == (1,)
    assert theme.output_spec == (
        "### 하는 일\n색, 글꼴, 간격을 정한다.\n\n### 산출물\n- 형태: (정하지 않음)\n\n"
        "### 그 외 설명\n- 기존 서비스 색을 그대로 쓴다."
    )
    assert result["changes"][0].startswith(f"나눔: {ids['화면 설계']} 화면 설계 → ")
    assert "{" not in result["changes"][0]  # 임시 id 가 진짜 id 로 바뀜
    assert result["summary"].startswith(f'계획 {plan_id} "쇼핑몰 화면" 을 고쳤습니다. 노드 4개, 간선 3개.')


def test_should_split_in_parallel_between_same_neighbors():
    plan_id, ids = _plan_with_chain()
    into = [{"title": "웹 화면", "scope": "웹"}, {"title": "앱 화면", "scope": "앱"}]
    edit_plan(plan_id, {"ops": [{"op": "split", "node_id": ids["화면 설계"], "order": "parallel", "into": into}]})
    assert _titled_edges(plan_id) == {
        ("요구사항", "웹 화면"), ("요구사항", "앱 화면"), ("웹 화면", "화면 구현"), ("앱 화면", "화면 구현"),
    }  # fmt: skip


def test_should_merge_nodes_and_keep_outer_links_only():
    plan_id, ids = _plan_with_chain()
    op = {
        "op": "merge",
        "node_ids": [ids["화면 설계"], ids["화면 구현"]],
        "title": "화면 만들기",
        "scope": "설계와 구현",
    }
    edit_plan(plan_id, {"ops": [op]})
    assert _titled_edges(plan_id) == {("요구사항", "화면 만들기")}
    assert _node(plan_id, "화면 만들기").kind is NodeKind.DOCUMENT  # 첫 노드의 종류


def test_should_insert_confirm_node_between_two_nodes_without_persona():
    plan_id, ids = _plan_with_chain()
    op = {"op": "insert", "after": ids["화면 설계"], "before": ids["화면 구현"], "kind": "hitl",
          "title": "화면 설계 확인", "scope": "사용자가 화면 설계를 확인한다."}  # fmt: skip
    edit_plan(plan_id, {"ops": [op]})
    assert _titled_edges(plan_id) == {
        ("요구사항", "화면 설계"),
        ("화면 설계", "화면 설계 확인"),
        ("화면 설계 확인", "화면 구현"),
    }
    assert _node(plan_id, "화면 설계 확인").persona_ids == ()


def test_should_remove_node_and_link_before_to_after():
    plan_id, ids = _plan_with_chain()
    result = edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]})
    assert result["ok"] is True
    assert _titled_edges(plan_id) == {("요구사항", "화면 구현")}


def test_should_update_only_given_sections():
    plan_id, ids = _plan_with_chain()
    op = {"op": "update", "node_id": ids["화면 구현"], "add_note": "응답은 항상 {data, error} 로 감싼다."}
    result = edit_plan(plan_id, {"ops": [op]})
    spec = _node(plan_id, "화면 구현").output_spec
    assert spec.endswith("### 그 외 설명\n- 응답은 항상 {data, error} 로 감싼다.")
    assert spec.startswith("### 하는 일\n화면 구현\n\n### 산출물\n- 형태: 문서")
    assert result["changes"] == [f"고침: {ids['화면 구현']} 화면 구현"]
    assert len(_titled_edges(plan_id)) == 2


def test_should_refuse_cycle_and_send_nothing():
    plan_id, ids = _plan_with_chain()
    before = MockPlanApiReader().get_plan(plan_id)
    result = edit_plan(plan_id, {"ops": [{"op": "link", "from": ids["화면 구현"], "to": ids["요구사항"]}]})
    assert result["ok"] is False and "순환" in result["reason"]
    assert MockPlanApiReader().get_plan(plan_id) == before


def test_should_refuse_when_plan_is_not_reviewing_or_op_is_wrong():
    approved_id, ids = _plan_with_chain(PlanStatus.APPROVED)
    refused = edit_plan(approved_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]})
    assert refused["ok"] is False and "검토 중이 아니라(approved)" in refused["reason"]
    plan_id, ids = _plan_with_chain()
    assert "1 번째 동작을 읽지 못했습니다" in edit_plan(plan_id, {"ops": [{"op": "jump"}]})["reason"]
    assert "노드 999 가 계획에 없습니다" in edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": 999}]})["reason"]


def test_should_show_plan_nodes_with_spec_and_edges():
    plan_id, ids = _plan_with_chain()
    shown = show_plan(plan_id)
    assert shown["status"] == "reviewing" and shown["persona_ids"] == [1]
    assert shown["nodes"][0] == {
        "node_id": ids["요구사항"], "title": "요구사항", "kind": "document", "persona_ids": [1],
        "output_spec": SPEC.format("요구사항"),
    }  # fmt: skip
    assert {"from": ids["요구사항"], "to": ids["화면 설계"]} in shown["edges"]


def test_should_not_refuse_for_problems_that_were_already_there():
    plan_id, ids = _plan_with_chain()
    MockPlanApiWriter().update_node(plan_id, ids["화면 구현"], NodeChange(persona_ids=()))  # 원래 있던 문제: 담당 없음
    rename = {"op": "update", "node_id": ids["화면 구현"], "title": "화면 개발"}
    result = edit_plan(plan_id, {"ops": [rename, {"op": "remove", "node_id": ids["화면 설계"]}]})
    assert result["ok"] is True, result
    assert result["problems"] == [f"노드 {ids['화면 구현']} 화면 개발: 담당 페르소나가 없습니다"]


def test_should_give_persona_when_confirm_node_becomes_work_and_merge_same_id_once():
    plan_id, ids = _plan_with_chain()
    insert = {"op": "insert", "after": ids["화면 설계"], "kind": "hitl", "title": "확인", "scope": "확인"}
    edit_plan(plan_id, {"ops": [insert]})
    confirm_id = _node(plan_id, "확인").node_id
    assert edit_plan(plan_id, {"ops": [{"op": "update", "node_id": confirm_id, "kind": "document"}]})["ok"] is True
    assert _node(plan_id, "확인").persona_ids == (1,)
    merge = {
        "op": "merge",
        "node_ids": [ids["요구사항"], ids["요구사항"], ids["화면 설계"]],
        "title": "설계",
        "scope": "s",
    }
    assert edit_plan(plan_id, {"ops": [merge]})["ok"] is True
