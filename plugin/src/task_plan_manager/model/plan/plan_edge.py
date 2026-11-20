"""노드 사이의 선행 관계. from 노드가 끝나야 to 노드를 시작한다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanEdge:
    edge_id: int
    from_node_id: int
    to_node_id: int
