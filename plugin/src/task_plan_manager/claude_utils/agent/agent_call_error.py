"""도구를 쓰는 claude -p 가 실패함. 종료 코드가 0 이 아님, 시간 초과, 오류 답, 빈 답."""

from __future__ import annotations


class AgentCallError(RuntimeError):
    """메시지는 실패한 노드의 이유로 사용자에게 보인다. 짧게 적는다."""
