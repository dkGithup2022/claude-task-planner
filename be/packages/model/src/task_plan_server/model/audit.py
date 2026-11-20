from datetime import UTC, datetime
from typing import Protocol


def utcnow() -> datetime:
    """도메인·Entity 가 공통으로 쓰는 현재 시각. tz-aware UTC."""
    return datetime.now(UTC)


class AuditFields(Protocol):
    created_at: datetime
    updated_at: datetime
