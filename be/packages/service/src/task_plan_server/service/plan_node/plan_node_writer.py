from abc import ABC, abstractmethod

from task_plan_server.model.plan_node.plan_node import PlanNode
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity

from .dto.plan_node_create_command import PlanNodeCreateCommand
from .dto.plan_node_update_command import PlanNodeUpdateCommand


class PlanNodeWriter(ABC):
    @abstractmethod
    def create(self, command: PlanNodeCreateCommand) -> PlanNodeIdentity:
        """새 노드. 상태는 todo. 계획이 있는지는 부르는 쪽(Usecase)이 먼저 본다."""

    @abstractmethod
    def update(self, command: PlanNodeUpdateCommand) -> PlanNode:
        """값이 있는 필드만 바꾼다. 노드가 없거나 다른 계획의 노드면 PlanNodeNotFoundException."""

    @abstractmethod
    def delete(self, identity: PlanNodeIdentity) -> None:
        """노드를 지운다. 없으면 PlanNodeNotFoundException. 닿은 간선은 지우지 않는다."""
