from dataclasses import dataclass
from datetime import datetime

from .plan_node_counts import PlanNodeCounts
from .plan_status import PlanStatus


@dataclass(frozen=True, slots=True)
class PlanSummary:
    """계획 목록의 한 줄. 노드와 간선 대신 상태별 노드 수를 담는다."""

    plan_id: int
    title: str
    status: PlanStatus
    persona_ids: tuple[int, ...]
    node_counts: PlanNodeCounts
    created_at: datetime
    updated_at: datetime
