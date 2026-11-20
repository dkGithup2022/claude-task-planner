from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_db_engine(
    url: str, *, pool_size: int = 20, max_overflow: int = 20, echo: bool = False
) -> Engine:
    return create_engine(
        url, pool_size=pool_size, max_overflow=max_overflow, pool_pre_ping=True, echo=echo
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autobegin=False,  # 트랜잭션은 @transactional 이 명시적으로 연다
        expire_on_commit=False,  # commit 후에도 객체를 재조회 없이 읽는다
        autoflush=True,
    )
