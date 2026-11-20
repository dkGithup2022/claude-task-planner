from dataclasses import dataclass
from datetime import datetime
from typing import Self

from task_plan_server.model.audit import utcnow

from .plan_edge_read import PlanEdgeRead


@dataclass(frozen=True, slots=True)
class PlanEdge:
    """앞 노드가 끝나야 뒤 노드를 시작한다는 관계. 만들고 지우기만 하고 고치지 않는다.

    자기 자신을 잇는 간선이나 순환은 검사하지 않는다 (CLI 가 확정·실행 전에 본다).
    """

    edge_id: int | None
    plan_id: int
    from_node_id: int  # 이 노드가 끝나야
    to_node_id: int  # 이 노드를 시작한다
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, plan_id: int, from_node_id: int, to_node_id: int) -> Self:
        now = utcnow()
        return cls(None, plan_id, from_node_id, to_node_id, now, now)

    def to_read(self) -> PlanEdgeRead:
        if self.edge_id is None:
            raise ValueError("plan edge must be persisted before to_read")
        return PlanEdgeRead(
            self.edge_id,
            self.plan_id,
            self.from_node_id,
            self.to_node_id,
            self.created_at,
            self.updated_at,
        )
