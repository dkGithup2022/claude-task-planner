"""고치기를 거절함. 계획 저장소에는 아무것도 보내지 않았다."""

from __future__ import annotations


class PlanEditRefusedError(ValueError):
    """고치기를 거절함. 계획 저장소에는 아무것도 보내지 않았다. 메시지에 이유를 담는다."""
