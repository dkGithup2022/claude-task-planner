"""계획 저장소 쓰기. 지금은 mock, 나중에 서버 API."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_edge import PlanEdge
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.dto.node_change import NodeChange


class PlanApiWriter(ABC):
    @abstractmethod
    def create_plan(self, new_plan: NewPlan) -> Plan:
        """새 계획 (POST /plans). 상태는 drafting, 노드와 간선은 비어 있다. id 는 저장소가 준다."""

    @abstractmethod
    def add_node(self, plan_id: int, new_node: NewNode) -> PlanNode:
        """노드 하나 저장 (POST /plans/{plan_id}/nodes). 상태는 todo. 계획이 없으면 PlanNotFoundError."""

    @abstractmethod
    def add_edge(self, plan_id: int, from_node_id: int, to_node_id: int) -> PlanEdge:
        """간선 하나 저장. 같은 간선이 있으면 그것을 돌려준다. 양 끝 노드가 없으면 PlanApiError."""

    @abstractmethod
    def update_node(self, plan_id: int, node_id: int, change: NodeChange) -> PlanNode:
        """노드 고치기 (PATCH). change 에서 값이 있는 필드만 바꾼다. 노드가 없으면 PlanApiError."""

    @abstractmethod
    def delete_node(self, plan_id: int, node_id: int) -> None:
        """노드와 그 노드에 닿은 간선을 지운다. 이미 없으면 아무것도 하지 않는다."""

    @abstractmethod
    def delete_edge(self, plan_id: int, edge_id: int) -> None:
        """간선 하나를 지운다. 이미 없으면 아무것도 하지 않는다."""

    @abstractmethod
    def set_plan_status(self, plan_id: int, status: PlanStatus) -> Plan:
        """계획 상태 바꾸기 (PATCH /plans/{plan_id}/status, 가안). 허용하는 바꾸기인지는 부르는 쪽이 먼저 본다."""
