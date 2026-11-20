from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanIdentity:
    plan_id: int
