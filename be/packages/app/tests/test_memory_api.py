"""지식 API 를 실제 Postgres 에 띄운 앱으로 HTTP 로 부르는 시험."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from task_plan_server.service.memory.usecase.memory_search_terms_refresh_usecase import (
    MemorySearchTermsRefreshUsecase,
)


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


def test_search_accepts_limit_up_to_30_and_rejects_31_with_400(client: TestClient) -> None:
    body = {"kind": "plan", "query": "x", "persona_ids": [1], "theme": None}

    assert client.post("/api/memories/search", json={**body, "limit": 30}).status_code == 200
    assert client.post("/api/memories/search", json={**body, "limit": 31}).status_code == 400


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


def test_search_finds_word_with_particle_attached(client: TestClient) -> None:
    """한국어 형태소로 나눠 조사가 붙어도 찾는다 ("설계에서" 로 "설계" 지식)."""
    design = _memory(client, "plan", "API 설계", "엔드포인트마다 에러 코드를 함께 정한다", [1])
    _memory(client, "plan", "기획 문서 작성", "상위와 하위 기획으로 나눈다", [1])

    items = _search(client, query="설계에서 에러를")

    assert [item["memory_id"] for item in items] == [design]
    assert 0 < float(str(items[0]["score"])) <= 1


def test_search_uses_new_words_after_patch(client: TestClient) -> None:
    """고치면 검색용 낱말도 다시 만들어진다."""
    memory_id = _memory(client, "plan", "문서 작성 계획", "검토를 마지막에 두지 않는다", [1])
    assert _search(client, query="정합성") == []

    client.patch(f"/api/memories/{memory_id}", json={"body": "정합성 검증 노드를 따로 두지 않는다"})

    assert [item["memory_id"] for item in _search(client, query="정합성")] == [memory_id]
    assert _search(client, query="마지막") == []


def test_search_without_words_returns_nothing(client: TestClient) -> None:
    """검색어가 비었거나 숫자, 기호, 조사만 있으면 맞는 낱말이 없으므로 빈 결과."""
    _memory(client, "plan", "테이블 설계", "배열은 별도 테이블", [1])

    for query in ("", "에서는", "404", "!!"):
        assert _search(client, query=query) == []


def test_refresh_fills_only_memories_without_search_terms(
    client: TestClient, engine: Engine
) -> None:
    """DB 에 직접 넣어 낱말이 빈 지식만 채운다. 고친 시각은 그대로."""
    memory_id = _memory(client, "plan", "API 설계", "엔드포인트마다 에러 코드", [1])
    with engine.begin() as conn:
        clear = text("UPDATE memories SET search_tokens = ''::tsvector WHERE id = :id")
        conn.execute(clear, {"id": memory_id})
        before = conn.execute(
            text("SELECT updated_at FROM memories WHERE id = :id"), {"id": memory_id}
        ).scalar_one()
    assert _search(client, query="엔드포인트") == []

    with client.app.state.dishka_container() as request_container:  # type: ignore[attr-defined]
        filled = request_container.get(MemorySearchTermsRefreshUsecase).execute()

    assert filled == 1
    assert [item["memory_id"] for item in _search(client, query="엔드포인트")] == [memory_id]
    with engine.begin() as conn:
        after = conn.execute(
            text("SELECT updated_at FROM memories WHERE id = :id"), {"id": memory_id}
        ).scalar_one()
    assert after == before
