"""계획 저장소에 쓰지 못함."""

from __future__ import annotations


class PlanApiError(RuntimeError):
    """요청이 계획과 맞지 않아 쓰지 못했다. 예: 없는 노드를 잇는 간선. 메시지에 무엇을 요청했는지 담는다."""
