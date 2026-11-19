"""검토 중으로 바꿀 수 없는 상태의 계획을 보여 주려 함."""

from __future__ import annotations


class PlanNotShowableError(RuntimeError):
    """작성 중이나 검토 중이 아닌 계획(승인, 불허, 실행 중, 끝남)이다. 메시지에 계획 id 와 상태를 담는다."""
