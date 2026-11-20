from sqlalchemy.orm import DeclarativeBase

from task_plan_server.model.audit import utcnow  # noqa: F401  Entity 모듈이 여기서 re-import 한다


class Base(DeclarativeBase):
    """모든 Entity 의 부모. 공통 컬럼은 두지 않는다 — 각 Entity 가 4필드를 직접 선언 (C-3)."""
