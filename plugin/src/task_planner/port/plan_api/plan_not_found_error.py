"""찾는 계획이 계획 저장소에 없음."""

from __future__ import annotations


class PlanNotFoundError(LookupError):
    """계획 id 로 찾지 못했다. 메시지에 계획 id 를 담는다."""
