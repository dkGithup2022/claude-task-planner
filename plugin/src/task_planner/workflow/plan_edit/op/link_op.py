"""간선 하나를 더한다: to 노드가 from 노드의 산출물을 받아 쓴다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LinkOp:
    """간선 하나를 더한다: to 노드가 from 노드의 산출물을 받아 쓴다."""

    from_node_id: int
    to_node_id: int
