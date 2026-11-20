"""tpm-trial mock 데이터를 서버 DB 에 원래 id 그대로 넣는다 (사용자, 2026-11-20).

API 로는 id 를 정할 수 없으므로 DB 에 직접 넣는다. 넣은 뒤 다음 id 가 mock 의 마지막 번호
(ids.json) 다음부터 이어지게 맞춘다. 대상 테이블에 행이 하나라도 있으면 아무것도 하지 않고 멈춘다.

시각: 계획은 created_at 을 지킨다. 시각이 없는 지식·노드·간선은 넣는 시각을 쓴다.

실행 (be/ 에서): uv run python scripts/import_mock_data.py [mock 폴더]
DB 주소는 APP_DATABASE_URL (.env) 에서 읽는다.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import Connection, create_engine, text

DEFAULT_MOCK_DIR = Path(__file__).resolve().parent.parent / "seed" / "tpm-trial"

# 행이 있으면 멈출 테이블과, 다음 id 를 맞출 테이블 → ids.json 의 키
TABLES = ("personas", "memories", "plans", "plan_nodes", "plan_edges")
SEQUENCE_FLOORS = {"plans": "plan", "plan_nodes": "node", "plan_edges": "edge"}


class TargetNotEmptyError(RuntimeError):
    """대상 테이블에 이미 행이 있음."""


def import_mock(conn: Connection, mock_dir: Path) -> dict[str, int]:
    """mock 데이터를 넣고 테이블마다 넣은 행 수를 돌려준다. conn 의 트랜잭션은 부르는 쪽이 연다."""
    _require_empty(conn)
    now = datetime.now(UTC)
    personas = _read(mock_dir / "personas.json")["personas"]
    memories = _read(mock_dir / "memories.json")["memories"]
    plans = [_read(path) for path in sorted((mock_dir / "plans").glob("*.json"))]
    floors = _read(mock_dir / "ids.json")

    for persona in personas:
        conn.execute(
            text(
                "INSERT INTO personas (id, name, description, is_deleted, created_at, updated_at)"
                " VALUES (:id, :name, :description, false, :now, :now)"
            ),
            {
                "id": persona["persona_id"],
                "name": persona["name"],
                "description": persona.get("description") or "",
                "now": now,
            },
        )
    for memory in memories:
        _insert_memory(conn, memory, now)
    node_count = edge_count = 0
    for plan in plans:
        _insert_plan(conn, plan, now)
        node_count += len(plan["nodes"])
        edge_count += len(plan["edges"])

    for table in TABLES:
        floor = int(floors.get(SEQUENCE_FLOORS.get(table, ""), 0))
        conn.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'),"
                f" GREATEST((SELECT COALESCE(max(id), 0) FROM {table}), :floor, 1))"
            ),
            {"floor": floor},
        )
    return {
        "personas": len(personas),
        "memories": len(memories),
        "plans": len(plans),
        "plan_nodes": node_count,
        "plan_edges": edge_count,
    }


def _require_empty(conn: Connection) -> None:
    filled = [
        table
        for table in TABLES
        if conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one() > 0
    ]
    if filled:
        raise TargetNotEmptyError(f"이미 데이터가 있는 테이블: {', '.join(filled)}")


def _insert_memory(conn: Connection, memory: dict[str, Any], now: datetime) -> None:
    conn.execute(
        text(
            "INSERT INTO memories (id, kind, theme, body, is_deleted, created_at, updated_at)"
            " VALUES (:id, :kind, :theme, :body, false, :now, :now)"
        ),
        {
            "id": memory["memory_id"],
            "kind": memory["kind"],
            "theme": memory["theme"],
            "body": memory["body"],
            "now": now,
        },
    )
    for position, persona_id in enumerate(memory.get("persona_ids") or []):
        conn.execute(
            text(
                "INSERT INTO memory_personas (memory_id, persona_id, position)"
                " VALUES (:memory_id, :persona_id, :position)"
            ),
            {"memory_id": memory["memory_id"], "persona_id": persona_id, "position": position},
        )
    for position, source in enumerate(memory.get("source") or []):
        conn.execute(
            text(
                "INSERT INTO memory_sources (memory_id, quote, plan_id, position)"
                " VALUES (:memory_id, :quote, :plan_id, :position)"
            ),
            {
                "memory_id": memory["memory_id"],
                "quote": source["quote"],
                "plan_id": source["plan_id"],
                "position": position,
            },
        )


def _insert_plan(conn: Connection, plan: dict[str, Any], now: datetime) -> None:
    created_at = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
    conn.execute(
        text(
            "INSERT INTO plans (id, title, request, status, is_deleted, created_at, updated_at)"
            " VALUES (:id, :title, :request, :status, false, :created_at, :created_at)"
        ),
        {
            "id": plan["plan_id"],
            "title": plan["title"],
            "request": plan["request"],
            "status": plan["status"],
            "created_at": created_at,
        },
    )
    for position, persona_id in enumerate(plan.get("persona_ids") or []):
        conn.execute(
            text(
                "INSERT INTO plan_personas (plan_id, persona_id, position)"
                " VALUES (:plan_id, :persona_id, :position)"
            ),
            {"plan_id": plan["plan_id"], "persona_id": persona_id, "position": position},
        )
    for node in plan["nodes"]:
        conn.execute(
            text(
                "INSERT INTO plan_nodes (id, plan_id, title, kind, output_spec, status,"
                " is_deleted, created_at, updated_at) VALUES (:id, :plan_id, :title, :kind,"
                " :output_spec, :status, false, :now, :now)"
            ),
            {
                "id": node["node_id"],
                "plan_id": plan["plan_id"],
                "title": node["title"],
                "kind": node["kind"],
                "output_spec": node["output_spec"],
                "status": node["status"],
                "now": now,
            },
        )
        for position, persona_id in enumerate(node.get("persona_ids") or []):
            conn.execute(
                text(
                    "INSERT INTO plan_node_personas (node_id, persona_id, position)"
                    " VALUES (:node_id, :persona_id, :position)"
                ),
                {"node_id": node["node_id"], "persona_id": persona_id, "position": position},
            )
    for edge in plan["edges"]:
        conn.execute(
            text(
                "INSERT INTO plan_edges (id, plan_id, from_node_id, to_node_id, is_deleted,"
                " created_at, updated_at) VALUES (:id, :plan_id, :from_id, :to_id, false,"
                " :now, :now)"
            ),
            {
                "id": edge["edge_id"],
                "plan_id": plan["plan_id"],
                "from_id": edge["from_node_id"],
                "to_id": edge["to_node_id"],
                "now": now,
            },
        )


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    load_dotenv()
    mock_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MOCK_DIR
    engine = create_engine(os.environ["APP_DATABASE_URL"])
    try:
        with engine.begin() as conn:  # 하나라도 실패하면 모두 되돌린다
            counts = import_mock(conn, mock_dir)
    except TargetNotEmptyError as stopped:
        print(f"멈춤: {stopped}. 빈 DB 에만 넣는다.", file=sys.stderr)
        sys.exit(1)
    finally:
        engine.dispose()
    print("넣음: " + ", ".join(f"{table} {count}" for table, count in counts.items()))


if __name__ == "__main__":
    main()
