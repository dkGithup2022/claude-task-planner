"""참여 페르소나로 넣을 페르소나가 하나도 없음."""

from __future__ import annotations


class NoPersonaError(RuntimeError):
    """페르소나 목록이 비어 계획을 등록하지 못했다. 페르소나를 먼저 만들어야 한다."""
