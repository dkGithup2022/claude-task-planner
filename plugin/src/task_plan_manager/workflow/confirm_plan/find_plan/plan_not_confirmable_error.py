"""확정할 계획을 정하지 못함. 명령에 id 가 없거나, 계획이 없거나, 검토 중이 아니거나, 보여 준 기록이 없다."""

from __future__ import annotations


class PlanNotConfirmableError(RuntimeError):
    """메시지는 메인 세션이 사용자에게 그대로 보인다. 무엇이 문제이고 어떻게 하면 되는지 적는다."""
