from dataclasses import dataclass
from datetime import datetime

from .node_kind import NodeKind
from .plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanNodeRead:
    node_id: int
    plan_id: int
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]
    output_spec: str
    status: PlanNodeStatus
    created_at: datetime
    updated_at: datetime
