from abc import ABC, abstractmethod

from task_plan_server.model.plan.plan import Plan
from task_plan_server.model.plan.plan_identity import PlanIdentity

from .dto.plan_create_command import PlanCreateCommand
from .dto.plan_status_change_command import PlanStatusChangeCommand


class PlanWriter(ABC):
    @abstractmethod
    def create(self, command: PlanCreateCommand) -> PlanIdentity:
        """새 계획. 상태는 drafting, 노드와 간선은 없다."""

    @abstractmethod
    def change_status(self, command: PlanStatusChangeCommand) -> Plan:
        """계획 상태를 바꾼다. 순서는 검사하지 않는다. 없으면 PlanNotFoundException."""
