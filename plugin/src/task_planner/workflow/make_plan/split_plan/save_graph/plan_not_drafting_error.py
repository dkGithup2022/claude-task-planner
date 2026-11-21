"""작성 중이 아닌 계획에 노드를 새로 저장하려 함."""

from __future__ import annotations


class PlanNotDraftingError(RuntimeError):
    """검토 중 이후의 계획은 노드를 지우고 다시 만들지 않는다. 메시지에 계획 id 와 지금 상태를 담는다."""
