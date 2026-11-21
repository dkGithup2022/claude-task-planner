"""계획의 지금 상태에서 그 결정(승인 / 불허)으로 바꿀 수 없음."""

from __future__ import annotations


class DecisionNotAllowedError(RuntimeError):
    """find_plan 뒤에 다른 곳에서 상태가 바뀐 경우에 생긴다. 메시지에 계획 id 와 지금 상태를 담는다."""
