from abc import ABC, abstractmethod

from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_edge.plan_edge import PlanEdge
from task_plan_server.model.plan_edge.plan_edge_identity import PlanEdgeIdentity
from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity


class PlanEdgeRepository(ABC):
    @abstractmethod
    def find_by_plan_id(self, plan_identity: PlanIdentity) -> list[PlanEdgeRead]:
        """계획의 간선 전부. 지운 간선은 뺀다. edge_id 순. 없으면 []."""

    @abstractmethod
    def delete_by_node_id(self, node_identity: PlanNodeIdentity) -> None:
        """앞이나 뒤가 이 노드인 간선을 모두 soft-delete. 없으면 no-op."""

    @abstractmethod
    def save(self, edge: PlanEdge) -> PlanEdge:
        """간선 저장 (신규만. 간선은 고치지 않는다). 저장한 간선을 id 와 함께 돌려준다."""

    @abstractmethod
    def find_by_ends(
        self, plan_identity: PlanIdentity, from_node_id: int, to_node_id: int
    ) -> PlanEdge | None:
        """계획에서 앞·뒤 노드가 같은 간선. 지운 간선은 뺀다."""

    @abstractmethod
    def find_write_by_id(self, identity: PlanEdgeIdentity) -> PlanEdge | None:
        """간선 Write 모델 조회. 지운 간선은 없음으로 본다."""

    @abstractmethod
    def delete_by_id(self, identity: PlanEdgeIdentity) -> None:
        """간선 soft-delete. 이미 지웠으면 no-op."""
