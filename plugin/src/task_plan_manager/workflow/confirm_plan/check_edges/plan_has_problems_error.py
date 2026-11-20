"""확정하기 전에 고쳐야 할 노드·간선 문제가 있음."""

from __future__ import annotations


class PlanHasProblemsError(RuntimeError):
    """메시지에 문제 목록과, 고친 뒤 같은 명령을 다시 부르라는 안내를 담는다. 메인 세션이 그대로 보인다."""
