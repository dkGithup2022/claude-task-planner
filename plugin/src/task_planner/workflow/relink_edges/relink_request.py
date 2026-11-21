"""간선 다시 정하기의 입력: 무엇이 바뀌었는지, 바뀐 노드와 앞뒤 노드, 바뀌기 전 간선, 사용자가 직접 정한 간선."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.relink_edges.relink_node import RelinkNode

Edge = tuple[int, int]  # (앞 노드 id, 뒤 노드 id)


@dataclass(frozen=True, slots=True)
class RelinkRequest:
    change: str  # 바꾼 내용. 동작이 여럿이면 줄마다 하나
    original_nodes: tuple[RelinkNode, ...]  # 지워지거나 바뀌기 전의 노드
    changed_nodes: tuple[RelinkNode, ...]  # 이번에 생기거나 바뀐 노드
    neighbor_nodes: tuple[RelinkNode, ...]  # 바뀌기 전 원래 노드의 선행·후행 노드 (한 단계)
    previous_edges: tuple[Edge, ...]  # 바뀌기 전, 위 노드들 사이의 간선 가운데 다시 정할 것
    user_links: tuple[Edge, ...] = ()  # 사용자가 이으라고 한 간선. 반드시 남긴다
    user_unlinks: tuple[Edge, ...] = ()  # 사용자가 끊으라고 한 간선. 다시 잇지 않는다
    fixed_edges: tuple[Edge, ...] = ()  # 범위 안에서 그대로 남는 간선. 프롬프트에 보이고, 답과 상관없이 남긴다
    outside_edges: tuple[Edge, ...] = ()  # 범위 밖 노드에 닿은 지금 간선. 프롬프트에 넣지 않고 순환 검사에만 쓴다

    def scope_ids(self) -> set[int]:
        """간선을 다시 정하는 노드: 바뀐 노드와 앞뒤 노드."""
        return {node.node_id for node in (*self.changed_nodes, *self.neighbor_nodes)}
