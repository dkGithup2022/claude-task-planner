from dataclasses import dataclass
from datetime import datetime

from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead

from .plan_status import PlanStatus


@dataclass(frozen=True, slots=True)
class PlanRead:
    """계획과 그 계획의 노드, 간선 전부."""

    plan_id: int
    title: str
    request: str
    persona_ids: tuple[int, ...]
    status: PlanStatus
    nodes: tuple[PlanNodeRead, ...]
    edges: tuple[PlanEdgeRead, ...]
    created_at: datetime
    updated_at: datetime
