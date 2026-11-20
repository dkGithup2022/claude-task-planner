from abc import ABC, abstractmethod

from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_node.plan_node import PlanNode
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead


class PlanNodeRepository(ABC):
    @abstractmethod
    def find_by_plan_id(self, plan_identity: PlanIdentity) -> list[PlanNodeRead]:
        """계획의 노드 전부. 지운 노드는 뺀다. node_id 순. 없으면 []."""

    @abstractmethod
    def save(self, node: PlanNode) -> PlanNode:
        """노드 저장 (신규·수정). 담당 페르소나 순서를 지킨다. 저장한 노드를 id 와 함께 돌려준다."""

    @abstractmethod
    def find_write_by_id(self, identity: PlanNodeIdentity) -> PlanNode | None:
        """노드 Write 모델 조회. 지운 노드는 없음으로 본다."""

    @abstractmethod
    def delete_by_id(self, identity: PlanNodeIdentity) -> None:
        """노드 soft-delete. 이미 지웠으면 no-op. 닿은 간선은 지우지 않는다 (부르는 쪽이 지운다)."""
