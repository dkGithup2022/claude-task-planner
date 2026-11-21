"""save_graph 의 결과: local_id 와 서버 id 의 대응, 저장한 간선 수, 다시 수행하며 지운 노드 수."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SavedGraph:
    node_ids: dict[str, int]  # local_id → 계획 저장소가 준 node_id
    edge_count: int
    removed_node_count: int  # 앞선 시도가 남긴 노드를 지운 수. 처음이면 0
