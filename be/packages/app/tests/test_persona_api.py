"""페르소나 API 를 실제 Postgres 에 띄운 앱으로 HTTP 로 부르는 시험."""

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text


def _insert_persona(engine: Engine, name: str, deleted: bool = False) -> int:
    """만들기 API 가 생기기 전에 목록을 시험하려고 DB 에 직접 넣는다."""
    with engine.begin() as conn:
        return int(
            conn.execute(
                text(
                    "INSERT INTO personas (name, description, is_deleted, created_at, updated_at)"
                    " VALUES (:name, '설명', :deleted, now(), now()) RETURNING id"
                ),
                {"name": name, "deleted": deleted},
            ).scalar_one()
        )


def _memory(client: TestClient, persona_ids: list[int]) -> int:
    body = {"kind": "plan", "theme": "t", "body": "b", "persona_ids": persona_ids, "source": []}
    return int(client.post("/api/memories", json=body).json()["memory_id"])


def _plan(client: TestClient, persona_ids: list[int]) -> int:
    body = {"title": "t", "request": "r", "persona_ids": persona_ids}
    return int(client.post("/api/plans", json=body).json()["plan_id"])


def _node(client: TestClient, plan_id: int, persona_ids: list[int]) -> int:
    body = {"title": "n", "kind": "document", "persona_ids": persona_ids, "output_spec": "s"}
    return int(client.post(f"/api/plans/{plan_id}/nodes", json=body).json()["node_id"])


def test_list_personas_with_counts(client: TestClient, engine: Engine) -> None:
    first = _insert_persona(engine, "dankim-persona")
    second = _insert_persona(engine, "be-developer")
    _insert_persona(engine, "지운 페르소나", deleted=True)
    _memory(client, [first])
    _memory(client, [first, second])
    client.delete(f"/api/memories/{_memory(client, [second])}")  # 지운 지식은 세지 않는다
    _plan(client, [first])
    node_only_plan = _plan(client, [first])
    _node(client, node_only_plan, [second])  # 노드 담당만 쓰는 계획도 센다
    other_plan = _plan(client, [first])
    deleted_node = _node(client, other_plan, [second])
    client.delete(f"/api/plans/{other_plan}/nodes/{deleted_node}")  # 지운 노드는 세지 않는다

    response = client.get("/api/personas")

    assert response.status_code == 200
    assert response.json() == {
        "personas": [
            {
                "persona_id": first,
                "name": "dankim-persona",
                "description": "설명",
                "memory_count": 2,
                "plan_count": 3,
            },
            {
                "persona_id": second,
                "name": "be-developer",
                "description": "설명",
                "memory_count": 1,
                "plan_count": 1,
            },
        ]
    }


def test_list_personas_empty(client: TestClient) -> None:
    assert client.get("/api/personas").json() == {"personas": []}


def test_create_persona_and_list(client: TestClient) -> None:
    response = client.post("/api/personas", json={"name": "be-developer", "description": "백엔드"})

    assert response.status_code == 201
    persona_id = response.json()["persona_id"]
    assert client.get("/api/personas").json()["personas"] == [
        {
            "persona_id": persona_id,
            "name": "be-developer",
            "description": "백엔드",
            "memory_count": 0,
            "plan_count": 0,
        }
    ]


def test_create_persona_with_same_name_is_409(client: TestClient) -> None:
    client.post("/api/personas", json={"name": "be-developer", "description": ""})

    response = client.post("/api/personas", json={"name": "be-developer", "description": "x"})

    assert response.status_code == 409
    assert response.json()["error"] == "PersonaNameDuplicatedException"
    assert response.json()["message"] == "이름이 be-developer 인 페르소나가 이미 있습니다"


def test_create_persona_rejects_empty_name_with_400(client: TestClient) -> None:
    assert client.post("/api/personas", json={"name": "", "description": ""}).status_code == 400


def _create(client: TestClient, name: str, description: str = "설명") -> int:
    body = {"name": name, "description": description}
    return int(client.post("/api/personas", json=body).json()["persona_id"])


def test_update_persona_changes_only_sent_fields(client: TestClient) -> None:
    persona_id = _create(client, "be-developer", "백엔드")

    renamed = client.patch(f"/api/personas/{persona_id}", json={"name": "be-dev"})
    described = client.patch(f"/api/personas/{persona_id}", json={"description": "서버 개발"})

    assert renamed.status_code == 200
    assert described.json() == {"persona_id": persona_id}
    persona = client.get("/api/personas").json()["personas"][0]
    assert (persona["name"], persona["description"]) == ("be-dev", "서버 개발")


def test_update_persona_name_conflict_and_missing(client: TestClient) -> None:
    first = _create(client, "dankim-persona")
    _create(client, "be-developer")

    same_as_self = client.patch(f"/api/personas/{first}", json={"name": "dankim-persona"})
    conflict = client.patch(f"/api/personas/{first}", json={"name": "be-developer"})
    missing = client.patch("/api/personas/999999", json={"name": "x"})

    assert same_as_self.status_code == 200
    assert conflict.status_code == 409
    assert missing.status_code == 404


def test_delete_unused_persona_and_reuse_name(client: TestClient) -> None:
    persona_id = _create(client, "be-developer")

    response = client.delete(f"/api/personas/{persona_id}")

    assert response.status_code == 204
    assert client.get("/api/personas").json() == {"personas": []}
    assert (
        client.post("/api/personas", json={"name": "be-developer", "description": ""}).status_code
        == 201
    )


def test_delete_persona_in_use_is_409_with_counts(client: TestClient) -> None:
    persona_id = _create(client, "dankim-persona")
    _memory(client, [persona_id])
    _memory(client, [persona_id])
    plan_id = _plan(client, [])
    _node(client, plan_id, [persona_id])

    response = client.delete(f"/api/personas/{persona_id}")

    assert response.status_code == 409
    assert response.json()["error"] == "PersonaInUseException"
    assert response.json()["message"] == "지식 2개, 계획 1개가 이 페르소나를 씁니다"
    assert len(client.get("/api/personas").json()["personas"]) == 1


def test_delete_missing_persona_is_404(client: TestClient) -> None:
    assert client.delete("/api/personas/999999").status_code == 404
