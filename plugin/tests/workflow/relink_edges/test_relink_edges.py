"""relink_edges: 입력 JSON 모양, 출력 스키마, 받은 간선 거르기(범위 밖, 자기 자신, 중복, 끊은 간선, 순환, 이은 간선)."""

import json

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.claude_utils.prompt.prompt_output_converter import PromptOutputConverter
from task_plan_manager.workflow.relink_edges.prompt_relink_edges_edge import RelinkEdgesEdge
from task_plan_manager.workflow.relink_edges.prompt_relink_edges_output import RelinkEdgesOutput
from task_plan_manager.workflow.relink_edges.relink_edges import RELINK_EDGES, relink_edges
from task_plan_manager.workflow.relink_edges.relink_node import RelinkNode
from task_plan_manager.workflow.relink_edges.relink_request import RelinkRequest

SPEC = "### 하는 일\n{}\n\n### 산출물\n- 형태: 코드 변경\n{} 코드\n\n### 그 외 설명\n(없음)"


def _node(node_id: int, title: str) -> RelinkNode:
    return RelinkNode(node_id, title, "code", SPEC.format(f"{title}을 한다.", title))


# 39 를 41, 42, 43 으로 나눔. 앞뒤 노드 35, 37
REQUEST = RelinkRequest(
    change='39 "화면 구현" 을 41, 42, 43 으로 나눔',
    original_nodes=(_node(39, "화면 구현"),),
    changed_nodes=(_node(41, "와이어프레임"), _node(42, "컴포넌트"), _node(43, "API 연결")),
    neighbor_nodes=(_node(35, "화면 구조 파악"), _node(37, "API 구현")),
    previous_edges=((35, 39), (37, 39)),
    user_links=((35, 42),),
    user_unlinks=((37, 41),),
)


def _caller(edges: list[tuple[int, int]], seen: list[str]):
    def caller(spec, user_input):
        seen.append(user_input)
        output = RelinkEdgesOutput([RelinkEdgesEdge(from_id, to_id) for from_id, to_id in edges])
        return output, PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_send_nodes_with_spec_sections_and_previous_edges():
    seen: list[str] = []
    relink_edges(REQUEST, _caller([], seen))
    sent = json.loads(seen[0])
    assert sent["change"] == '39 "화면 구현" 을 41, 42, 43 으로 나눔'
    assert sent["original_nodes"][0] == {
        "id": 39, "title": "화면 구현", "kind": "code", "does": "화면 구현을 한다.",
        "output": {"form": "코드 변경", "contents": "화면 구현 코드"}, "notes": "",
    }  # fmt: skip
    assert [node["id"] for node in sent["changed_nodes"]] == [41, 42, 43]
    assert [node["id"] for node in sent["neighbor_nodes"]] == [35, 37]
    assert sent["previous_edges"] == [{"from": 35, "to": 39}, {"from": 37, "to": 39}]
    assert sent["user_edges"] == {"link": [{"from": 35, "to": 42}], "unlink": [{"from": 37, "to": 41}]}


def test_should_ask_output_with_from_id_and_to_id():
    schema = PromptOutputConverter().to_schema(RELINK_EDGES.output_type)
    assert schema["properties"]["edges"]["items"]["required"] == ["from_id", "to_id"]
    assert RELINK_EDGES.model == "opus"


def test_should_filter_proposed_edges_and_keep_user_links():
    proposed = [
        (35, 41), (41, 42), (42, 43), (37, 43),
        (39, 41),  # 지워진 원래 노드
        (43, 43),  # 자기 자신
        (41, 42),  # 중복
        (37, 41),  # 사용자가 끊음
        (43, 41),  # 순환 (41 → 42 → 43 → 41)
    ]  # fmt: skip
    result = relink_edges(REQUEST, _caller(proposed, []))
    assert result.edges == ((35, 42), (35, 41), (41, 42), (42, 43), (37, 43))
    assert result.dropped == (
        ((39, 41), "바뀐 노드와 앞뒤 노드가 아닌 노드라 버림"),
        ((43, 43), "자기 자신을 잇는 간선이라 버림"),
        ((41, 42), "이미 있는 간선이라 버림"),
        ((37, 41), "사용자가 끊은 간선이라 버림"),
        ((43, 41), "넣으면 순환이 생겨 넣지 않음"),
    )
