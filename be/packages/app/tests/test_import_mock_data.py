"""mock 데이터 넣기 스크립트를 시험용 Postgres 에 돌리고 API 로 읽어 본다."""

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "import_mock_data.py"
spec = importlib.util.spec_from_file_location("import_mock_data", SCRIPT)
assert spec is not None and spec.loader is not None
import_mock_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_mock_data)


def test_import_keeps_ids_and_is_readable_through_api(client: TestClient, engine: Engine) -> None:
    with engine.begin() as conn:
        counts = import_mock_data.import_mock(conn, import_mock_data.DEFAULT_MOCK_DIR)

    assert counts == {"personas": 2, "memories": 7, "plans": 1, "plan_nodes": 10, "plan_edges": 29}
    plan = client.get("/api/plans/11").json()
    assert (plan["status"], plan["created_at"]) == ("done", "2026-11-20T04:16:15Z")
    assert len(plan["nodes"]) == 10 and len(plan["edges"]) == 29
    assert {node["status"] for node in plan["nodes"]} == {"done"}
    personas = client.get("/api/personas").json()["personas"]
    assert [(p["persona_id"], p["memory_count"], p["plan_count"]) for p in personas] == [
        (1, 7, 1),
        (2, 1, 0),
    ]
    first = client.get("/api/memories/1").json()
    assert first["theme"] == "테이블 설계" and len(first["source"]) == 4
    listed = client.get("/api/memories").json()["items"]
    assert {item["memory_id"]: item["appended_count"] for item in listed}[1] == 3


def test_import_continues_ids_after_mock_counters(client: TestClient, engine: Engine) -> None:
    with engine.begin() as conn:
        import_mock_data.import_mock(conn, import_mock_data.DEFAULT_MOCK_DIR)

    plan_id = client.post("/api/plans", json={"title": "t", "request": "r", "persona_ids": [1]})
    node_id = client.post(
        f"/api/plans/{plan_id.json()['plan_id']}/nodes",
        json={"title": "n", "kind": "document", "persona_ids": [1], "output_spec": "s"},
    )
    memory = client.post(
        "/api/memories",
        json={"kind": "plan", "theme": "t", "body": "b", "persona_ids": [1], "source": []},
    )

    assert plan_id.json()["plan_id"] == 12
    assert node_id.json()["node_id"] == 57
    assert memory.json()["memory_id"] == 8


def test_import_refuses_non_empty_db(client: TestClient, engine: Engine) -> None:
    client.post("/api/personas", json={"name": "이미 있음", "description": ""})

    with pytest.raises(import_mock_data.TargetNotEmptyError), engine.begin() as conn:
        import_mock_data.import_mock(conn, import_mock_data.DEFAULT_MOCK_DIR)
