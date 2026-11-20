from datetime import UTC, datetime


def to_utc_text(value: datetime) -> str:
    """API 문서와 같은 초 단위 UTC 문자열. 예: 2026-11-20T04:16:15Z.

    CLI 는 이 문자열을 그대로 갖고 있으므로 모양을 문서에 맞춘다.
    """
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
