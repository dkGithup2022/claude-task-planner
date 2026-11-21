"""plan show / plan edit: 묶음 동작을 미리 적용하고, 나누기·합치기·넣기·빼기면 간선을 다시 정한다.
점검을 통과하면 mock 계획 저장소에 보낸다.
간선 다시 정하기(claude -p)는 가짜 caller 로 바꾼다. 무엇을 넘겼는지 sent 에 남긴다."""

import json

from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.claude_utils.prompt.prompt_call_error import PromptCallError
from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_planner.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_planner.workflow.plan_edit.edit_plan import edit_plan, show_plan
from task_planner.workflow.relink_edges.prompt_relink_edges_edge import RelinkEdgesEdge
from task_planner.workflow.relink_edges.prompt_relink_edges_output import RelinkEdgesOutput

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


class FakeRelink:
    """간선 다시 정하기 대신. answer(sent) 가 돌려준 (앞, 뒤) 목록을 간선으로 낸다. 넘긴 입력 JSON 은 sent 에 남는다."""

    def __init__(self, answer=lambda sent: []):
        self.answer = answer
        self.sent: list[dict] = []

    def __call__(self, spec, user_input):
        sent = json.loads(user_input)
        self.sent.append(sent)
        edges = [RelinkEdgesEdge(from_id, to_id) for from_id, to_id in self.answer(sent)]
        return RelinkEdgesOutput(edges), PromptCallRecord({"user": user_input}, {"ok": True})


def _not_called(spec, user_input):
    raise AssertionError("간선 다시 정하기를 부르면 안 됨")


def _ids_of(sent, key):
    return {node["title"]: node["id"] for node in sent[key]}


def test_should_split_node_and_use_relinked_edges():
    plan_id, ids = _plan_with_chain()
    ops = {"ops": [{"op": "split", "node_id": ids["화면 설계"], "into": [
        {"title": "와이어프레임 설계", "kind": "document", "does": "화면별 배치와 이동 흐름을 정한다.",
         "output": {"form": "문서", "contents": "화면별 와이어프레임"}},
        {"title": "디자인 테마 설계", "kind": "research", "does": "색, 글꼴, 간격을 정한다.",
         "notes": "기존 서비스 색을 그대로 쓴다."},
    ]}]}  # fmt: skip

    def answer(sent):  # 요구사항 → 와이어프레임, 요구사항 → 테마, 둘 다 → 화면 구현
        new = _ids_of(sent, "changed_nodes")
        return [(ids["요구사항"], new["와이어프레임 설계"]), (ids["요구사항"], new["디자인 테마 설계"]),
                (new["와이어프레임 설계"], ids["화면 구현"]), (new["디자인 테마 설계"], ids["화면 구현"])]  # fmt: skip

    relink = FakeRelink(answer)
    result = edit_plan(plan_id, ops, relink)

    assert result["ok"] is True and result["problems"] == []
    sent = relink.sent[0]
    assert sent["change"].startswith(f'{ids["화면 설계"]} "화면 설계" 을 -1, -2 으로 나눔')
    assert [node["title"] for node in sent["original_nodes"]] == ["화면 설계"]
    assert [node["title"] for node in sent["neighbor_nodes"]] == ["요구사항", "화면 구현"]
    assert sent["previous_edges"] == [
        {"from": ids["요구사항"], "to": ids["화면 설계"]},
        {"from": ids["화면 설계"], "to": ids["화면 구현"]},
    ]
    assert _titled_edges(plan_id) == {
        ("요구사항", "와이어프레임 설계"), ("요구사항", "디자인 테마 설계"),
        ("와이어프레임 설계", "화면 구현"), ("디자인 테마 설계", "화면 구현"),
    }  # fmt: skip
    wireframe, theme = _node(plan_id, "와이어프레임 설계"), _node(plan_id, "디자인 테마 설계")
    assert wireframe.kind is NodeKind.DOCUMENT and theme.kind is NodeKind.RESEARCH and theme.persona_ids == (1,)
    assert wireframe.output_spec == (
        "### 하는 일\n화면별 배치와 이동 흐름을 정한다.\n\n### 산출물\n- 형태: 문서\n화면별 와이어프레임\n\n"
        "### 그 외 설명\n(없음)"
    )
    assert theme.output_spec.endswith(
        "### 산출물\n- 형태: (정하지 않음)\n\n### 그 외 설명\n- 기존 서비스 색을 그대로 쓴다."
    )
    assert result["changes"][0].startswith(f"나눔: {ids['화면 설계']} 화면 설계 → ")
    wireframe_id, theme_id = wireframe.node_id, theme.node_id
    assert result["changes"][1] == (
        f"이음: {ids['요구사항']} → {wireframe_id}, {ids['요구사항']} → {theme_id}, "
        f"{wireframe_id} → {ids['화면 구현']}, {theme_id} → {ids['화면 구현']}"
    )
    assert (
        result["changes"][2] == f"끊음: {ids['요구사항']} → {ids['화면 설계']}, {ids['화면 설계']} → {ids['화면 구현']}"
    )
    assert not any("{" in change for change in result["changes"])  # 임시 id 가 진짜 id 로 바뀜
    assert result["summary"].startswith(f'계획 {plan_id} "쇼핑몰 화면" 을 고쳤습니다. 노드 4개, 간선 4개.')


def test_should_keep_edge_between_neighbors_when_relink_keeps_it_on_insert():
    plan_id, ids = _plan_with_chain()
    op = {"op": "insert", "after": ids["화면 설계"], "before": ids["화면 구현"], "kind": "hitl",
          "title": "화면 설계 확인", "does": "사용자가 화면 설계를 확인한다."}  # fmt: skip

    def answer(sent):
        new = _ids_of(sent, "changed_nodes")["화면 설계 확인"]
        return [(ids["화면 설계"], new), (new, ids["화면 구현"]), (ids["화면 설계"], ids["화면 구현"])]

    relink = FakeRelink(answer)
    edit_plan(plan_id, {"ops": [op]}, relink)
    where = f"{ids['화면 설계']} 과 {ids['화면 구현']} 사이에 "
    assert relink.sent[0]["change"] == where + '-1 "화면 설계 확인" 를 넣음'
    assert relink.sent[0]["previous_edges"] == [{"from": ids["화면 설계"], "to": ids["화면 구현"]}]
    assert _titled_edges(plan_id) == {
        ("요구사항", "화면 설계"),
        ("화면 설계", "화면 설계 확인"),
        ("화면 설계 확인", "화면 구현"),
        ("화면 설계", "화면 구현"),
    }
    assert _node(plan_id, "화면 설계 확인").persona_ids == ()


def test_should_widen_insert_to_nodes_around_place_and_keep_their_other_edges():
    """e2e5 와 같은 모양: 넣는 자리의 앞뒤 노드까지 넘기고, 새 노드에 닿는 간선과 자리 사이 간선만 다시 정한다."""
    plan_id, ids = _plan_with_chain()
    writer = MockPlanApiWriter()
    test_id = writer.add_node(plan_id, NewNode("화면 테스트", NodeKind.CODE, (1,), SPEC.format("테스트"))).node_id
    writer.add_edge(plan_id, ids["화면 구현"], test_id)
    writer.add_edge(plan_id, ids["화면 설계"], test_id)
    op = {"op": "insert", "after": ids["화면 설계"], "before": ids["화면 구현"], "kind": "document",
          "title": "화면 명세", "does": "화면별 입력과 표시 규칙을 정한다."}  # fmt: skip

    def answer(sent):  # 명세는 설계를 받아 구현과 테스트에 준다. 설계 → 구현은 남긴다. 고정 간선은 답하지 않는다
        new = _ids_of(sent, "changed_nodes")["화면 명세"]
        return [(ids["화면 설계"], new), (new, ids["화면 구현"]), (new, test_id), (ids["화면 설계"], ids["화면 구현"])]

    relink = FakeRelink(answer)
    result = edit_plan(plan_id, {"ops": [op]}, relink)
    sent = relink.sent[0]
    assert result["ok"] is True
    assert [node["title"] for node in sent["neighbor_nodes"]] == ["요구사항", "화면 설계", "화면 구현", "화면 테스트"]
    assert sent["previous_edges"] == [{"from": ids["화면 설계"], "to": ids["화면 구현"]}]
    assert sent["fixed_edges"] == [
        {"from": ids["요구사항"], "to": ids["화면 설계"]},
        {"from": ids["화면 설계"], "to": test_id},
        {"from": ids["화면 구현"], "to": test_id},
    ]
    assert _titled_edges(plan_id) == {
        ("요구사항", "화면 설계"),
        ("화면 설계", "화면 명세"),
        ("화면 명세", "화면 구현"),
        ("화면 명세", "화면 테스트"),
        ("화면 설계", "화면 구현"),
        ("화면 설계", "화면 테스트"),
        ("화면 구현", "화면 테스트"),
    }
    assert result["changes"][1:] == [
        f"이음: {ids['화면 설계']} → {{new}}, {{new}} → {ids['화면 구현']}, {{new}} → {test_id}".replace(
            "{new}", str(_node(plan_id, "화면 명세").node_id)
        )
    ]


def test_should_merge_nodes_and_use_relinked_edges():
    plan_id, ids = _plan_with_chain()
    op = {
        "op": "merge",
        "node_ids": [ids["화면 설계"], ids["화면 구현"]],
        "title": "화면 만들기",
        "does": "설계와 구현",
    }
    relink = FakeRelink(lambda sent: [(ids["요구사항"], _ids_of(sent, "changed_nodes")["화면 만들기"])])
    edit_plan(plan_id, {"ops": [op]}, relink)
    assert [node["title"] for node in relink.sent[0]["original_nodes"]] == ["화면 설계", "화면 구현"]
    assert [node["title"] for node in relink.sent[0]["neighbor_nodes"]] == ["요구사항"]
    assert _titled_edges(plan_id) == {("요구사항", "화면 만들기")}
    assert _node(plan_id, "화면 만들기").kind is NodeKind.DOCUMENT  # 첫 노드의 종류


def test_should_remove_node_and_let_relink_decide_neighbors():
    plan_id, ids = _plan_with_chain()
    relink = FakeRelink(lambda sent: [(ids["요구사항"], ids["화면 구현"])])
    result = edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]}, relink)
    assert result["ok"] is True and relink.sent[0]["changed_nodes"] == []
    assert _titled_edges(plan_id) == {("요구사항", "화면 구현")}
    assert result["changes"][0] == f"뺌: {ids['화면 설계']} 화면 설계"


def test_should_update_only_given_sections_without_relink():
    plan_id, ids = _plan_with_chain()
    op = {"op": "update", "node_id": ids["화면 구현"], "add_note": "응답은 항상 {data, error} 로 감싼다.",
          "output": {"form": "코드 변경", "contents": "화면 코드"}}  # fmt: skip
    result = edit_plan(plan_id, {"ops": [op]}, _not_called)
    spec = _node(plan_id, "화면 구현").output_spec
    assert spec == (
        "### 하는 일\n화면 구현\n\n### 산출물\n- 형태: 코드 변경\n화면 코드\n\n"
        "### 그 외 설명\n- 응답은 항상 {data, error} 로 감싼다."
    )
    assert result["changes"] == [f"고침: {ids['화면 구현']} 화면 구현"]
    assert len(_titled_edges(plan_id)) == 2


def test_should_not_reconnect_edge_the_user_unlinked_in_same_edit():
    plan_id, ids = _plan_with_chain()
    ops = {"ops": [
        {"op": "unlink", "from": ids["화면 설계"], "to": ids["화면 구현"]},
        {"op": "insert", "after": ids["화면 설계"], "before": ids["화면 구현"], "kind": "hitl",
         "title": "확인", "does": "확인"},
    ]}  # fmt: skip
    relink = FakeRelink(
        lambda sent: [(ids["화면 설계"], ids["화면 구현"]), (ids["화면 설계"], -1), (-1, ids["화면 구현"])]
    )
    result = edit_plan(plan_id, ops, relink)
    assert relink.sent[0]["user_edges"]["unlink"] == [{"from": ids["화면 설계"], "to": ids["화면 구현"]}]
    assert result["ok"] is True and ("화면 설계", "화면 구현") not in _titled_edges(plan_id)


def test_should_drop_cycle_through_node_outside_scope_instead_of_refusing():
    plan_id, ids = _plan_with_chain()
    writer = MockPlanApiWriter()
    outside = writer.add_node(plan_id, NewNode("범위 밖", NodeKind.CODE, (1,), SPEC.format("밖"))).node_id
    writer.add_edge(plan_id, ids["요구사항"], outside)  # 요구사항 → 범위 밖 → 화면 구현
    writer.add_edge(plan_id, outside, ids["화면 구현"])
    relink = FakeRelink(lambda sent: [(ids["화면 구현"], ids["요구사항"])])  # 범위 밖을 거치면 순환
    result = edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]}, relink)
    assert result["ok"] is True, result
    assert ("화면 구현", "요구사항") not in _titled_edges(plan_id)


def test_should_not_call_relink_when_insert_has_no_place():
    plan_id, ids = _plan_with_chain()
    op = {"op": "insert", "kind": "document", "title": "메모", "does": "메모를 쓴다"}
    assert edit_plan(plan_id, {"ops": [op]}, _not_called)["ok"] is True


def test_should_refuse_when_relink_fails_and_send_nothing():
    plan_id, ids = _plan_with_chain()
    before = MockPlanApiReader().get_plan(plan_id)

    def failing(spec, user_input):
        raise PromptCallError("claude -p 시간 초과", PromptCallRecord({}, {}))

    result = edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]}, failing)
    assert result["ok"] is False and "간선을 다시 정하지 못해 고치지 않았습니다" in result["reason"]
    assert MockPlanApiReader().get_plan(plan_id) == before


def test_should_refuse_cycle_and_send_nothing():
    plan_id, ids = _plan_with_chain()
    before = MockPlanApiReader().get_plan(plan_id)
    result = edit_plan(plan_id, {"ops": [{"op": "link", "from": ids["화면 구현"], "to": ids["요구사항"]}]}, _not_called)
    assert result["ok"] is False and "순환" in result["reason"]
    assert MockPlanApiReader().get_plan(plan_id) == before


def test_should_refuse_when_plan_is_not_reviewing_or_op_is_wrong():
    approved_id, ids = _plan_with_chain(PlanStatus.APPROVED)
    refused = edit_plan(approved_id, {"ops": [{"op": "remove", "node_id": ids["화면 설계"]}]}, _not_called)
    assert refused["ok"] is False and "검토 중이 아니라(approved)" in refused["reason"]
    plan_id, ids = _plan_with_chain()
    assert "1 번째 동작을 읽지 못했습니다" in edit_plan(plan_id, {"ops": [{"op": "jump"}]}, _not_called)["reason"]
    missing = edit_plan(plan_id, {"ops": [{"op": "remove", "node_id": 999}]}, _not_called)
    assert "노드 999 가 계획에 없습니다" in missing["reason"]
    no_kind = {"op": "insert", "after": ids["요구사항"], "title": "확인", "does": "확인"}
    assert "kind 가 있어야 합니다" in edit_plan(plan_id, {"ops": [no_kind]}, _not_called)["reason"]


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
    relink = FakeRelink(lambda sent: [(ids["요구사항"], ids["화면 구현"])])
    result = edit_plan(plan_id, {"ops": [rename, {"op": "remove", "node_id": ids["화면 설계"]}]}, relink)
    assert result["ok"] is True, result
    assert result["problems"] == [f"노드 {ids['화면 구현']} 화면 개발: 담당 페르소나가 없습니다"]


def test_should_give_persona_when_confirm_node_becomes_work_and_merge_same_id_once():
    plan_id, ids = _plan_with_chain()
    insert = {"op": "insert", "after": ids["화면 설계"], "kind": "hitl", "title": "확인", "does": "확인"}
    edit_plan(plan_id, {"ops": [insert]}, FakeRelink(lambda sent: [(ids["화면 설계"], -1)]))
    confirm_id = _node(plan_id, "확인").node_id
    to_work = {"op": "update", "node_id": confirm_id, "kind": "document"}
    assert edit_plan(plan_id, {"ops": [to_work]}, _not_called)["ok"] is True
    assert _node(plan_id, "확인").persona_ids == (1,)
    merge = {
        "op": "merge",
        "node_ids": [ids["요구사항"], ids["요구사항"], ids["화면 설계"]],
        "title": "설계",
        "does": "s",
    }
    assert edit_plan(plan_id, {"ops": [merge]}, FakeRelink())["ok"] is True


def test_should_show_editing_then_feedback_turn_even_when_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "s")
    monkeypatch.chdir(tmp_path)
    plan_id, ids = _plan_with_chain()
    (tmp_path / ".plan" / str(plan_id)).mkdir(parents=True)  # 이 작업 폴더에서 등록한 계획
    edit_plan(plan_id, {"ops": [{"op": "update", "node_id": ids["화면 설계"], "title": "화면 설계 v2"}]}, _not_called)
    edit_plan(plan_id, {"ops": [{"op": "없는 동작"}]}, _not_called)

    records = (tmp_path / ".plan" / str(plan_id) / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    editing = [json.loads(line)["detail"]["editing_since"] is not None for line in records]
    assert editing == [True, False, True, False]
