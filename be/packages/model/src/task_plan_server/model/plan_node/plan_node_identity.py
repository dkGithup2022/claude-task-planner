from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanNodeIdentity:
    node_id: int
