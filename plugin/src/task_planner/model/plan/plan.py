"""계획 하나. 노드와 간선을 함께 담는다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_status import PlanStatus


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: int
    title: str
    request: str  # 명령서 본문 (md)
    persona_ids: tuple[int, ...]
    status: PlanStatus
    created_at: str
    nodes: tuple[PlanNode, ...]
    edges: tuple[PlanEdge, ...]

    def node(self, node_id: int) -> PlanNode:
        """id 로 찾은 노드. 없으면 KeyError."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(f"계획 {self.plan_id} 에 노드 {node_id} 가 없습니다")

    def prerequisites(self, node_id: int) -> tuple[int, ...]:
        """선행 노드: 간선으로 이 노드에 바로 이어진 앞 노드의 id. 그보다 더 앞의 노드는 넣지 않는다."""
        return tuple(edge.from_node_id for edge in self.edges if edge.to_node_id == node_id)

    def problems(self) -> tuple[str, ...]:
        """확정·실행 전에 고쳐야 할 문제. 순환, 간선 끝(없는 노드, 자기 자신, 같은 간선), 담당 없음. 없으면 빈 튜플."""
        return (*self._cycle_problems(), *self._edge_end_problems(), *self._persona_problems())

    def _cycle_problems(self) -> list[str]:
        """간선을 따라가다 처음 노드로 돌아오는 길마다 한 줄. 같은 노드들로 된 순환은 한 번만."""
        titles = {node.node_id: node.title for node in self.nodes}
        next_ids: dict[int, list[int]] = {node_id: [] for node_id in titles}
        for edge in self.edges:
            if edge.from_node_id in titles and edge.to_node_id in titles and edge.from_node_id != edge.to_node_id:
                next_ids[edge.from_node_id].append(edge.to_node_id)
        found: list[str] = []
        seen_cycles: set[frozenset[int]] = set()
        for start in titles:
            for cycle in _cycles_from(start, next_ids):
                if frozenset(cycle) not in seen_cycles:
                    seen_cycles.add(frozenset(cycle))
                    found.append(
                        "순환: " + " → ".join(f"{node_id} {titles[node_id]}" for node_id in [*cycle, cycle[0]])
                    )
        return found

    def _edge_end_problems(self) -> list[str]:
        """간선의 앞·뒤 노드가 없거나, 자기 자신을 잇거나, 같은 두 노드를 잇는 간선이 여럿인 경우."""
        node_ids = {node.node_id for node in self.nodes}
        found: list[str] = []
        edge_ids_by_pair: dict[tuple[int, int], list[int]] = {}
        for edge in self.edges:
            if edge.from_node_id not in node_ids:
                found.append(f"간선 {edge.edge_id}: 앞 노드 {edge.from_node_id} 가 계획에 없습니다")
            if edge.to_node_id not in node_ids:
                found.append(f"간선 {edge.edge_id}: 뒤 노드 {edge.to_node_id} 가 계획에 없습니다")
            if edge.from_node_id == edge.to_node_id:
                found.append(f"간선 {edge.edge_id}: 노드 {edge.from_node_id} 이 자기 자신을 잇습니다")
            edge_ids_by_pair.setdefault((edge.from_node_id, edge.to_node_id), []).append(edge.edge_id)
        for (from_id, to_id), edge_ids in edge_ids_by_pair.items():
            if len(edge_ids) > 1:
                joined = ", ".join(str(edge_id) for edge_id in edge_ids)
                found.append(f"간선 {joined}: 같은 노드를 잇습니다 ({from_id} → {to_id})")
        return found

    def _persona_problems(self) -> list[str]:
        """확인 노드(hitl)가 아닌데 담당 페르소나가 없는 노드."""
        return [
            f"노드 {node.node_id} {node.title}: 담당 페르소나가 없습니다"
            for node in self.nodes
            if node.kind is not NodeKind.HITL and not node.persona_ids
        ]


def _cycles_from(start: int, next_ids: dict[int, list[int]]) -> list[list[int]]:
    """start 에서 출발해 start 로 돌아오는 길들. 길은 start 부터 돌아오기 직전 노드까지."""
    cycles: list[list[int]] = []
    waiting: list[list[int]] = [[start]]
    while waiting:
        path = waiting.pop()
        for next_id in next_ids[path[-1]]:
            if next_id == start:
                cycles.append(path)
            elif next_id not in path and next_id > start:  # 더 작은 id 에서 시작하는 순환은 그 id 에서 찾는다
                waiting.append([*path, next_id])
    return cycles
