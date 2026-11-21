"""계획 상태 값을 사용자에게 보일 한국어로."""

from __future__ import annotations

LABELS = {
    "drafting": "작성 중",
    "reviewing": "검토 중",
    "approved": "승인",
    "rejected": "불허",
    "running": "실행 중",
    "done": "끝남",
}


def status_label(status: str) -> str:
    """모르는 값은 그대로 보인다."""
    return LABELS.get(status, status)
