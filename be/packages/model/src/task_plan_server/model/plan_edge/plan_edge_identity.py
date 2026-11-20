from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanEdgeIdentity:
    edge_id: int
