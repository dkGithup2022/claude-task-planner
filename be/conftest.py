from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.community.postgres import PostgresContainer

from task_plan_server.app.main import create_app
from task_plan_server.persistence import entities  # noqa: F401  metadata 완성
from task_plan_server.persistence.base import Base
from task_plan_server.persistence.session import create_session_factory

ROOT = Path(__file__).parent


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """testcontainers Postgres. DB 가 필요한 테스트가 처음 요청할 때만 기동된다."""
    with PostgresContainer("postgres:16-alpine", driver="psycopg") as pg:
        yield pg.get_connection_url()


@pytest.fixture(scope="session")
def engine(database_url: str) -> Iterator[Engine]:
    cfg = Config(str(ROOT / "packages" / "schema" / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(cfg, "head")
    engine = create_engine(database_url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return create_session_factory(engine)


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """외부 트랜잭션 + 세이브포인트 (Java 테스트 클래스 @Transactional 대응).

    테스트 안의 commit 은 전부 세이브포인트 해제라서, 끝나면 통째로 롤백된다.
    """
    with engine.connect() as conn:
        outer = conn.begin()
        s = Session(
            bind=conn,
            autobegin=False,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield s
        finally:
            s.close()
            outer.rollback()


# migration 이 시드를 넣는 참조 테이블 (예: categories). 비우면 다음 테스트가 시드 없이 돈다.
# 참조 테이블을 만드는 add-entity-specs 가 여기에 이름을 추가한다.
SEED_TABLES: set[str] = set()


@pytest.fixture
def truncate_all(engine: Engine) -> Iterator[None]:
    """동시성 테스트 전용. 실제 commit 을 허용하고 끝나면 시드 테이블을 뺀 전 테이블을 비운다."""
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name not in SEED_TABLES:
                conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))


@pytest.fixture
def client(
    database_url: str, engine: Engine, truncate_all: None, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """시험용 Postgres 에 붙은 앱. HTTP 로 부르고, 끝나면 truncate_all 이 테이블을 비운다."""
    monkeypatch.setenv("APP_DATABASE_URL", database_url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_LOG_FORMAT", "json")
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def personas(client: TestClient) -> dict[str, int]:
    """시험 데이터의 페르소나 둘. id 를 처음으로 돌려 비운 뒤 만들므로 1, 2 가 된다.

    지식·계획·노드가 persona_ids 를 검사하므로 그 시험들이 먼저 만든다.
    """
    made = {}
    for name in ("dankim-persona", "be-developer"):
        response = client.post("/api/personas", json={"name": name, "description": ""})
        made[name] = int(response.json()["persona_id"])
    assert made == {"dankim-persona": 1, "be-developer": 2}
    return made
