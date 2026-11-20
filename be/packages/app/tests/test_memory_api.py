"""지식 API 를 실제 Postgres 에 띄운 앱으로 HTTP 로 부르는 시험."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text


@pytest.fixture(autouse=True)
def _personas(personas: dict[str, int]) -> None:
    """페르소나 1, 2 를 먼저 만든다 (persona_ids 검사)."""


MEMORY_BODY = {
    "kind": "plan",
    "theme": "서비스 설계 문서 작성",
    "body": "서비스 설계 문서를 작성하는 계획에서 RDBMS 테이블 모델링이 필요하면 ...",
    "persona_ids": [1, 2],
    "source": [
        {"quote": "rdms 테이블 모델링이 필요한 경우에", "plan_id": 11},
        {"quote": "도메인 문서 다음에", "plan_id": 3},
    ],
}


def test_create_memory_returns_id_and_keeps_order(client: TestClient, engine: Engine) -> None:
    response = client.post("/api/memories", json=MEMORY_BODY)

    assert response.status_code == 201
    memory_id = response.json()["memory_id"]
    assert response.json() == {"memory_id": memory_id}
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT kind, theme FROM memories WHERE id = :id"), {"id": memory_id}
        ).one()
        sources = (
            conn.execute(
                text("SELECT plan_id FROM memory_sources WHERE memory_id = :id ORDER BY position"),
                {"id": memory_id},
            )
            .scalars()
            .all()
        )
    assert tuple(row) == ("plan", "서비스 설계 문서 작성")
    assert sources == [11, 3]


def test_create_memory_rejects_unknown_kind_and_empty_theme(client: TestClient) -> None:
    assert client.post("/api/memories", json={**MEMORY_BODY, "kind": "rule"}).status_code == 400
    assert client.post("/api/memories", json={**MEMORY_BODY, "theme": ""}).status_code == 400


def test_get_memory_returns_what_was_created(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]

    response = client.get(f"/api/memories/{memory_id}")

    assert response.status_code == 200
    assert response.json() == {"memory_id": memory_id, **MEMORY_BODY}


def test_get_missing_memory_is_404(client: TestClient) -> None:
    response = client.get("/api/memories/999999")

    assert response.status_code == 404
    assert response.json()["error"] == "MemoryNotFoundException"


def _updated_at(engine: Engine, memory_id: int) -> object:
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT updated_at FROM memories WHERE id = :id"), {"id": memory_id}
        ).scalar_one()


def test_patch_memory_with_cli_append_shape_keeps_other_fields(
    client: TestClient, engine: Engine
) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]
    before = _updated_at(engine, memory_id)
    appended = {
        "body": MEMORY_BODY["body"] + "\n\n****** KNOWLEDGE APPENDED 1 ********\n1. 새 규칙",
        "source": [*MEMORY_BODY["source"], {"quote": "새 근거", "plan_id": 12}],
    }

    response = client.patch(f"/api/memories/{memory_id}", json=appended)

    assert response.status_code == 200
    assert response.json() == {"memory_id": memory_id}
    assert client.get(f"/api/memories/{memory_id}").json() == {
        "memory_id": memory_id,
        **MEMORY_BODY,
        **appended,
    }
    assert _updated_at(engine, memory_id) > before


def test_patch_memory_with_web_shape(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]
    change = {"kind": "knowledge", "theme": "테이블 설계", "persona_ids": [2]}

    client.patch(f"/api/memories/{memory_id}", json=change)

    got = client.get(f"/api/memories/{memory_id}").json()
    assert got == {"memory_id": memory_id, **MEMORY_BODY, **change}


def test_patch_missing_memory_is_404_and_empty_theme_is_400(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]

    assert client.patch("/api/memories/999999", json={"body": "x"}).status_code == 404
    assert client.patch(f"/api/memories/{memory_id}", json={"theme": ""}).status_code == 400


def test_delete_memory_then_get_is_404(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]

    response = client.delete(f"/api/memories/{memory_id}")

    assert response.status_code == 204
    assert client.get(f"/api/memories/{memory_id}").status_code == 404


def test_delete_missing_or_deleted_memory_is_404(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]
    client.delete(f"/api/memories/{memory_id}")

    assert client.delete(f"/api/memories/{memory_id}").status_code == 404
    assert client.delete("/api/memories/999999").status_code == 404


def _memory(client: TestClient, kind: str, theme: str, body: str, persona_ids: list[int]) -> int:
    payload = {
        **MEMORY_BODY,
        "kind": kind,
        "theme": theme,
        "body": body,
        "persona_ids": persona_ids,
    }
    return int(client.post("/api/memories", json=payload).json()["memory_id"])


def _search(client: TestClient, **fields: object) -> list[dict[str, object]]:
    body = {
        "kind": "plan",
        "query": "기획 문서 작성",
        "persona_ids": [1],
        "theme": None,
        "limit": 10,
    }
    response = client.post("/api/memories/search", json={**body, **fields})
    assert response.status_code == 200
    return list(response.json()["items"])


def test_search_filters_by_kind_and_persona_and_orders_by_score(client: TestClient) -> None:
    best = _memory(client, "plan", "기획 문서 작성", "상위와 하위 기획으로 나눈다", [1])
    weaker = _memory(client, "plan", "문서 작성 계획", "검토를 마지막에 두지 않는다", [2, 1])
    _memory(client, "knowledge", "기획 문서 작성", "종류가 다르다", [1])
    _memory(client, "plan", "기획 문서 작성", "페르소나가 다르다", [2])
    _memory(client, "plan", "테이블 설계", "검색어와 맞지 않는다", [1])

    items = _search(client)

    assert [item["memory_id"] for item in items] == [best, weaker]
    assert items[0]["score"] > items[1]["score"] > 0
    assert set(items[0]) == {"memory_id", "kind", "theme", "body", "score"}


def test_search_with_theme_and_limit_and_skips_deleted(client: TestClient) -> None:
    first = _memory(client, "plan", "기획 문서 작성", "기획 하나", [1])
    second = _memory(client, "plan", "기획 문서 작성", "기획 둘", [1])
    _memory(client, "plan", "문서 작성 계획", "기획 문서", [1])
    client.delete(f"/api/memories/{first}")

    items = _search(client, theme="기획 문서 작성")
    limited = _search(client, limit=1)

    assert [item["memory_id"] for item in items] == [second]
    assert len(limited) == 1


def test_search_rejects_unknown_kind_with_400(client: TestClient) -> None:
    body = {"kind": "rule", "query": "x", "persona_ids": [1], "theme": None, "limit": 10}

    assert client.post("/api/memories/search", json=body).status_code == 400


def test_list_memories_newest_updated_first_with_fields(client: TestClient) -> None:
    older = _memory(client, "plan", "기획 문서 작성", "상위 기획", [1])
    newer = _memory(client, "knowledge", "테이블 설계", "FK 걸지 않는다", [1, 2])
    client.patch(
        f"/api/memories/{older}",
        json={"body": "상위 기획\n\n****** KNOWLEDGE APPENDED 1 ********\n하위 기획"},
    )

    body = client.get("/api/memories").json()

    assert [item["memory_id"] for item in body["items"]] == [older, newer]
    assert body["total"] == 2
    first = body["items"][0]
    assert first["appended_count"] == 1
    assert first["source_plan_ids"] == [11, 3]
    assert first["edited"] is True
    assert body["items"][1]["edited"] is False
    assert "body" not in first


def test_list_memories_filters_and_limit(client: TestClient) -> None:
    plan = _memory(client, "plan", "기획 문서 작성", "상위 기획", [1])
    knowledge = _memory(client, "knowledge", "테이블 설계", "기획 단계에서 정한다", [2])
    deleted = _memory(client, "plan", "기획 지운 것", "x", [1])
    client.delete(f"/api/memories/{deleted}")

    by_text = client.get("/api/memories", params={"q": "기획"}).json()
    by_kind = client.get("/api/memories", params={"kind": "plan"}).json()
    by_persona = client.get("/api/memories", params={"persona_id": 2}).json()
    limited = client.get("/api/memories", params={"limit": 1}).json()

    assert {item["memory_id"] for item in by_text["items"]} == {plan, knowledge}
    assert [item["memory_id"] for item in by_kind["items"]] == [plan]
    assert [item["memory_id"] for item in by_persona["items"]] == [knowledge]
    assert len(limited["items"]) == 1
    assert limited["total"] == 2


def test_list_memories_query_percent_is_literal(client: TestClient) -> None:
    _memory(client, "plan", "100% 완료 기준", "x", [1])
    _memory(client, "plan", "아무 작업", "x", [1])

    items = client.get("/api/memories", params={"q": "%"}).json()["items"]

    assert [item["theme"] for item in items] == ["100% 완료 기준"]


def test_unknown_or_deleted_persona_is_400_on_memory(client: TestClient) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]
    temp = client.post("/api/personas", json={"name": "임시", "description": ""}).json()
    client.delete(f"/api/personas/{temp['persona_id']}")

    create = client.post("/api/memories", json={**MEMORY_BODY, "persona_ids": [1, 77]})
    deleted = client.post(
        "/api/memories", json={**MEMORY_BODY, "persona_ids": [temp["persona_id"]]}
    )
    update = client.patch(f"/api/memories/{memory_id}", json={"persona_ids": [77]})

    assert create.status_code == 400
    assert create.json()["message"] == "페르소나 77 가 없습니다"
    assert deleted.status_code == 400
    assert update.status_code == 400
    assert client.get(f"/api/memories/{memory_id}").json()["persona_ids"] == [1, 2]


def test_patch_memory_keeps_child_rows_it_did_not_change(
    client: TestClient, engine: Engine
) -> None:
    memory_id = client.post("/api/memories", json=MEMORY_BODY).json()["memory_id"]

    def child_ids() -> tuple[list[int], list[int]]:
        with engine.connect() as conn:
            personas = (
                conn.execute(
                    text("SELECT id FROM memory_personas WHERE memory_id = :id ORDER BY id"),
                    {"id": memory_id},
                )
                .scalars()
                .all()
            )
            sources = (
                conn.execute(
                    text("SELECT id FROM memory_sources WHERE memory_id = :id ORDER BY id"),
                    {"id": memory_id},
                )
                .scalars()
                .all()
            )
        return list(personas), list(sources)

    before = child_ids()
    client.patch(f"/api/memories/{memory_id}", json={"theme": "새 작업 이름"})
    after_theme = child_ids()
    client.patch(f"/api/memories/{memory_id}", json={"persona_ids": MEMORY_BODY["persona_ids"]})
    after_same = child_ids()

    assert after_theme == before
    assert after_same == before
