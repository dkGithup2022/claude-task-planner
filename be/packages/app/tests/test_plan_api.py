"""계획 API 를 실제 Postgres 에 띄운 앱으로 HTTP 로 부르는 시험."""

import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text


@pytest.fixture(autouse=True)
def _personas(personas: dict[str, int]) -> None:
    """페르소나 1, 2 를 먼저 만든다 (persona_ids 검사)."""


PLAN_BODY = {
    "title": "계산기 웹 서비스 개발 전 문서 6종 작성",
    "request": "# 명령\n계산기 웹 서비스를 개발하기 전에 필요한 문서를 만듭니다.",
    "persona_ids": [1],
}


def test_create_plan_returns_id_drafting_and_seconds_utc_time(client: TestClient) -> None:
    response = client.post("/api/plans", json=PLAN_BODY)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"plan_id", "status", "created_at"}
    assert isinstance(body["plan_id"], int)
    assert body["status"] == "drafting"
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", body["created_at"])


def test_create_plan_gives_new_ids(client: TestClient) -> None:
    first = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    second = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    assert second > first


def test_create_plan_rejects_empty_title_with_400(client: TestClient) -> None:
    response = client.post("/api/plans", json={**PLAN_BODY, "title": ""})

    assert response.status_code == 400
    assert response.json()["error"] == "ValidationFailed"


def test_create_plan_rejects_missing_persona_ids_with_400(client: TestClient) -> None:
    body = {key: value for key, value in PLAN_BODY.items() if key != "persona_ids"}

    assert client.post("/api/plans", json=body).status_code == 400


def _insert_node(
    engine: Engine,
    plan_id: int,
    title: str,
    kind: str,
    persona_ids: list[int],
    deleted: bool = False,
) -> int:
    """노드 만들기 API 가 생기기 전에 GET 을 시험하려고 DB 에 직접 넣는다."""
    with engine.begin() as conn:
        node_id = conn.execute(
            text(
                "INSERT INTO plan_nodes (plan_id, title, kind, output_spec, status, is_deleted,"
                " created_at, updated_at) VALUES (:plan_id, :title, :kind, '### 하는 일\n...',"
                " 'todo', :deleted, now(), now()) RETURNING id"
            ),
            {"plan_id": plan_id, "title": title, "kind": kind, "deleted": deleted},
        ).scalar_one()
        for position, persona_id in enumerate(persona_ids):
            conn.execute(
                text(
                    "INSERT INTO plan_node_personas (node_id, persona_id, position)"
                    " VALUES (:node_id, :persona_id, :position)"
                ),
                {"node_id": node_id, "persona_id": persona_id, "position": position},
            )
    return int(node_id)


def _insert_edge(engine: Engine, plan_id: int, from_node_id: int, to_node_id: int) -> int:
    with engine.begin() as conn:
        edge_id = conn.execute(
            text(
                "INSERT INTO plan_edges (plan_id, from_node_id, to_node_id, is_deleted,"
                " created_at, updated_at) VALUES (:plan_id, :from_id, :to_id, false, now(), now())"
                " RETURNING id"
            ),
            {"plan_id": plan_id, "from_id": from_node_id, "to_id": to_node_id},
        ).scalar_one()
    return int(edge_id)


def test_get_new_plan_has_request_fields_and_empty_nodes_edges(client: TestClient) -> None:
    created = client.post("/api/plans", json={**PLAN_BODY, "persona_ids": [2, 1]}).json()

    response = client.get(f"/api/plans/{created['plan_id']}")

    assert response.status_code == 200
    assert response.json() == {
        "plan_id": created["plan_id"],
        "title": PLAN_BODY["title"],
        "request": PLAN_BODY["request"],
        "persona_ids": [2, 1],
        "status": "drafting",
        "created_at": created["created_at"],
        "nodes": [],
        "edges": [],
    }


def test_get_plan_returns_active_nodes_and_edges_of_that_plan_only(
    client: TestClient, engine: Engine
) -> None:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    other_plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    first = _insert_node(engine, plan_id, "상위 기획 작성", "document", [1, 2])
    second = _insert_node(engine, plan_id, "기획 확인", "hitl", [])
    _insert_node(engine, plan_id, "지운 노드", "code", [1], deleted=True)
    _insert_node(engine, other_plan_id, "다른 계획의 노드", "document", [1])
    edge_id = _insert_edge(engine, plan_id, first, second)

    body = client.get(f"/api/plans/{plan_id}").json()

    assert body["nodes"] == [
        {
            "node_id": first,
            "title": "상위 기획 작성",
            "kind": "document",
            "persona_ids": [1, 2],
            "output_spec": "### 하는 일\n...",
            "status": "todo",
        },
        {
            "node_id": second,
            "title": "기획 확인",
            "kind": "hitl",
            "persona_ids": [],
            "output_spec": "### 하는 일\n...",
            "status": "todo",
        },
    ]
    assert body["edges"] == [{"edge_id": edge_id, "from_node_id": first, "to_node_id": second}]


def test_get_missing_plan_is_404(client: TestClient) -> None:
    response = client.get("/api/plans/999999")

    assert response.status_code == 404
    assert response.json()["error"] == "PlanNotFoundException"


def test_change_plan_status_returns_changed_plan(client: TestClient) -> None:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    response = client.patch(f"/api/plans/{plan_id}/status", json={"status": "reviewing"})

    assert response.status_code == 200
    assert response.json()["status"] == "reviewing"
    assert response.json()["nodes"] == []
    assert client.get(f"/api/plans/{plan_id}").json()["status"] == "reviewing"


def test_change_plan_status_does_not_check_order(client: TestClient) -> None:
    """사용자가 대화로 상태를 되돌려 고칠 수 있어야 하므로, 끝난 계획도 되돌린다."""
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    client.patch(f"/api/plans/{plan_id}/status", json={"status": "done"})

    response = client.patch(f"/api/plans/{plan_id}/status", json={"status": "reviewing"})

    assert response.status_code == 200
    assert response.json()["status"] == "reviewing"


def test_change_status_of_missing_plan_is_404(client: TestClient) -> None:
    response = client.patch("/api/plans/999999/status", json={"status": "approved"})

    assert response.status_code == 404


def test_change_plan_status_rejects_unknown_status_with_400(client: TestClient) -> None:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    response = client.patch(f"/api/plans/{plan_id}/status", json={"status": "failed"})

    assert response.status_code == 400


NODE_BODY = {
    "title": "RDBMS 테이블 모델링",
    "kind": "document",
    "persona_ids": [1],
    "output_spec": "### 하는 일\n도메인 문서의 모델을 RDBMS 테이블 설계로 옮긴다.",
}


def test_create_node_returns_id_and_todo_and_shows_in_plan(client: TestClient) -> None:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    response = client.post(f"/api/plans/{plan_id}/nodes", json=NODE_BODY)

    assert response.status_code == 201
    created = response.json()
    assert set(created) == {"node_id", "status"}
    assert created["status"] == "todo"
    nodes = client.get(f"/api/plans/{plan_id}").json()["nodes"]
    assert nodes == [{"node_id": created["node_id"], **NODE_BODY, "status": "todo"}]


def test_create_node_on_missing_plan_is_404(client: TestClient) -> None:
    assert client.post("/api/plans/999999/nodes", json=NODE_BODY).status_code == 404


def test_create_node_rejects_unknown_kind_with_400(client: TestClient) -> None:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    response = client.post(f"/api/plans/{plan_id}/nodes", json={**NODE_BODY, "kind": "meeting"})

    assert response.status_code == 400


def _plan_with_node(client: TestClient) -> tuple[int, int]:
    plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    node_id = client.post(f"/api/plans/{plan_id}/nodes", json=NODE_BODY).json()["node_id"]
    return plan_id, node_id


def test_update_node_changes_only_sent_fields(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)

    response = client.patch(
        f"/api/plans/{plan_id}/nodes/{node_id}",
        json={"title": "와이어프레임 설계", "persona_ids": [2, 1]},
    )

    assert response.status_code == 200
    assert response.json() == {"node_id": node_id, "status": "todo"}
    node = client.get(f"/api/plans/{plan_id}").json()["nodes"][0]
    assert node == {
        **NODE_BODY,
        "node_id": node_id,
        "title": "와이어프레임 설계",
        "persona_ids": [2, 1],
        "status": "todo",
    }


def test_update_node_status_only_and_back(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)

    done = client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"status": "done"})
    back = client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"status": "todo"})

    assert done.json() == {"node_id": node_id, "status": "done"}
    assert back.json()["status"] == "todo"
    assert client.get(f"/api/plans/{plan_id}").json()["nodes"][0]["title"] == NODE_BODY["title"]


def test_update_node_of_other_plan_or_missing_is_404(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)
    other_plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    other = client.patch(f"/api/plans/{other_plan_id}/nodes/{node_id}", json={"status": "done"})
    missing = client.patch(f"/api/plans/{plan_id}/nodes/999999", json={"status": "done"})

    assert other.status_code == 404
    assert missing.status_code == 404


def test_update_node_rejects_empty_title_with_400(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)

    response = client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"title": ""})

    assert response.status_code == 400


def test_delete_node_removes_node_and_its_edges_only(client: TestClient, engine: Engine) -> None:
    plan_id, first = _plan_with_node(client)
    second = client.post(f"/api/plans/{plan_id}/nodes", json=NODE_BODY).json()["node_id"]
    third = client.post(f"/api/plans/{plan_id}/nodes", json=NODE_BODY).json()["node_id"]
    _insert_edge(engine, plan_id, first, second)
    _insert_edge(engine, plan_id, third, first)
    kept = _insert_edge(engine, plan_id, second, third)

    response = client.delete(f"/api/plans/{plan_id}/nodes/{first}")

    assert response.status_code == 204
    assert response.content == b""
    body = client.get(f"/api/plans/{plan_id}").json()
    assert [node["node_id"] for node in body["nodes"]] == [second, third]
    assert [edge["edge_id"] for edge in body["edges"]] == [kept]


def test_delete_node_again_or_missing_is_204(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)
    client.delete(f"/api/plans/{plan_id}/nodes/{node_id}")

    assert client.delete(f"/api/plans/{plan_id}/nodes/{node_id}").status_code == 204
    assert client.delete(f"/api/plans/{plan_id}/nodes/999999").status_code == 204


def test_delete_node_of_other_plan_keeps_it(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)
    other_plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    assert client.delete(f"/api/plans/{other_plan_id}/nodes/{node_id}").status_code == 204
    assert len(client.get(f"/api/plans/{plan_id}").json()["nodes"]) == 1


def _plan_with_two_nodes(client: TestClient) -> tuple[int, int, int]:
    plan_id, first = _plan_with_node(client)
    second = client.post(f"/api/plans/{plan_id}/nodes", json=NODE_BODY).json()["node_id"]
    return plan_id, first, second


def test_create_edge_returns_id_and_shows_in_plan(client: TestClient) -> None:
    plan_id, first, second = _plan_with_two_nodes(client)

    response = client.post(
        f"/api/plans/{plan_id}/edges", json={"from_node_id": first, "to_node_id": second}
    )

    assert response.status_code == 201
    edge_id = response.json()["edge_id"]
    assert response.json() == {"edge_id": edge_id}
    edges = client.get(f"/api/plans/{plan_id}").json()["edges"]
    assert edges == [{"edge_id": edge_id, "from_node_id": first, "to_node_id": second}]


def test_create_same_edge_returns_existing_with_200(client: TestClient) -> None:
    plan_id, first, second = _plan_with_two_nodes(client)
    body = {"from_node_id": first, "to_node_id": second}
    created = client.post(f"/api/plans/{plan_id}/edges", json=body).json()["edge_id"]

    again = client.post(f"/api/plans/{plan_id}/edges", json=body)

    assert again.status_code == 200
    assert again.json() == {"edge_id": created}
    assert len(client.get(f"/api/plans/{plan_id}").json()["edges"]) == 1


def test_create_edge_with_end_outside_plan_is_400(client: TestClient) -> None:
    plan_id, first, _ = _plan_with_two_nodes(client)
    _, other_node = _plan_with_node(client)

    other = client.post(
        f"/api/plans/{plan_id}/edges", json={"from_node_id": first, "to_node_id": other_node}
    )
    missing = client.post(
        f"/api/plans/{plan_id}/edges", json={"from_node_id": 999999, "to_node_id": first}
    )

    assert other.status_code == 400
    assert other.json()["error"] == "PlanEdgeEndNotInPlanException"
    assert missing.status_code == 400


def test_create_edge_on_missing_plan_is_404(client: TestClient) -> None:
    response = client.post("/api/plans/999999/edges", json={"from_node_id": 1, "to_node_id": 2})

    assert response.status_code == 404


def test_create_edge_to_deleted_node_is_400(client: TestClient) -> None:
    plan_id, first, second = _plan_with_two_nodes(client)
    client.delete(f"/api/plans/{plan_id}/nodes/{second}")

    response = client.post(
        f"/api/plans/{plan_id}/edges", json={"from_node_id": first, "to_node_id": second}
    )

    assert response.status_code == 400


def _plan_with_edge(client: TestClient) -> tuple[int, int]:
    plan_id, first, second = _plan_with_two_nodes(client)
    body = {"from_node_id": first, "to_node_id": second}
    edge_id = client.post(f"/api/plans/{plan_id}/edges", json=body).json()["edge_id"]
    return plan_id, edge_id


def test_delete_edge_removes_it_and_keeps_nodes(client: TestClient) -> None:
    plan_id, edge_id = _plan_with_edge(client)

    response = client.delete(f"/api/plans/{plan_id}/edges/{edge_id}")

    assert response.status_code == 204
    body = client.get(f"/api/plans/{plan_id}").json()
    assert body["edges"] == []
    assert len(body["nodes"]) == 2


def test_delete_edge_again_or_missing_is_204(client: TestClient) -> None:
    plan_id, edge_id = _plan_with_edge(client)
    client.delete(f"/api/plans/{plan_id}/edges/{edge_id}")

    assert client.delete(f"/api/plans/{plan_id}/edges/{edge_id}").status_code == 204
    assert client.delete(f"/api/plans/{plan_id}/edges/999999").status_code == 204


def test_delete_edge_of_other_plan_keeps_it(client: TestClient) -> None:
    plan_id, edge_id = _plan_with_edge(client)
    other_plan_id = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]

    assert client.delete(f"/api/plans/{other_plan_id}/edges/{edge_id}").status_code == 204
    assert len(client.get(f"/api/plans/{plan_id}").json()["edges"]) == 1


def test_update_node_can_clear_personas_and_change_kind_only(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)

    client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"persona_ids": [], "kind": "hitl"})

    node = client.get(f"/api/plans/{plan_id}").json()["nodes"][0]
    assert node["persona_ids"] == []
    assert node["kind"] == "hitl"
    assert node["output_spec"] == NODE_BODY["output_spec"]


def test_change_status_response_contains_nodes_and_edges(client: TestClient) -> None:
    plan_id, edge_id = _plan_with_edge(client)

    body = client.patch(f"/api/plans/{plan_id}/status", json={"status": "approved"}).json()

    assert len(body["nodes"]) == 2
    assert [edge["edge_id"] for edge in body["edges"]] == [edge_id]


def test_list_plans_newest_first_with_node_counts(client: TestClient, engine: Engine) -> None:
    older, first = _plan_with_node(client)
    for _ in range(2):
        client.post(f"/api/plans/{older}/nodes", json=NODE_BODY)
    client.patch(f"/api/plans/{older}/nodes/{first}", json={"status": "failed"})
    deleted_node = client.post(f"/api/plans/{older}/nodes", json=NODE_BODY).json()["node_id"]
    client.delete(f"/api/plans/{older}/nodes/{deleted_node}")
    newer = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    gone = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    with engine.begin() as conn:  # 계획 지우기 API 가 없어 DB 로 지운다
        conn.execute(text("UPDATE plans SET is_deleted = true WHERE id = :id"), {"id": gone})

    body = client.get("/api/plans").json()

    assert [plan["plan_id"] for plan in body["plans"]] == [newer, older]
    assert body["plans"][1]["node_counts"] == {
        "todo": 2,
        "running": 0,
        "done": 0,
        "failed": 1,
        "skipped": 0,
        "total": 3,
    }
    assert body["plans"][0]["node_counts"]["total"] == 0
    assert set(body["plans"][0]) == {
        "plan_id",
        "title",
        "status",
        "persona_ids",
        "created_at",
        "node_counts",
    }


def test_list_plans_by_status_and_limit(client: TestClient) -> None:
    running = client.post("/api/plans", json=PLAN_BODY).json()["plan_id"]
    client.patch(f"/api/plans/{running}/status", json={"status": "running"})
    client.post("/api/plans", json=PLAN_BODY)

    by_status = client.get("/api/plans", params={"status": "running"}).json()["plans"]
    limited = client.get("/api/plans", params={"limit": 1}).json()["plans"]

    assert [plan["plan_id"] for plan in by_status] == [running]
    assert len(limited) == 1
    assert client.get("/api/plans", params={"status": "failed"}).status_code == 400


def test_unknown_persona_is_400_on_plan_and_node(client: TestClient) -> None:
    plan_id, node_id = _plan_with_node(client)

    plan = client.post("/api/plans", json={**PLAN_BODY, "persona_ids": [1, 99]})
    node = client.post(f"/api/plans/{plan_id}/nodes", json={**NODE_BODY, "persona_ids": [99]})
    update = client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"persona_ids": [2, 98]})
    status_only = client.patch(f"/api/plans/{plan_id}/nodes/{node_id}", json={"status": "done"})

    assert plan.status_code == 400
    assert plan.json() == {
        "status": 400,
        "error": "UnknownPersonaException",
        "message": "페르소나 99 가 없습니다",
    }
    assert node.status_code == 400
    assert update.json()["message"] == "페르소나 98 가 없습니다"
    assert status_only.status_code == 200  # persona_ids 를 보내지 않으면 보지 않는다
