from abc import ABC, abstractmethod

from task_plan_server.model.plan_edge.plan_edge_identity import PlanEdgeIdentity

from .dto.plan_edge_create_command import PlanEdgeCreateCommand


class PlanEdgeWriter(ABC):
    @abstractmethod
    def create(self, command: PlanEdgeCreateCommand) -> PlanEdgeIdentity:
        """새 간선. 양 끝 노드와 같은 간선은 부르는 쪽(Usecase)이 먼저 본다."""

    @abstractmethod
    def delete(self, identity: PlanEdgeIdentity) -> None:
        """간선을 지운다. 없으면 PlanEdgeNotFoundException."""
