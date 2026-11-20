from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PlanEdgeRead:
    edge_id: int
    plan_id: int
    from_node_id: int
    to_node_id: int
    created_at: datetime
    updated_at: datetime
