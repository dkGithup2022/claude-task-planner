from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanEdgeCreateCommand:
    plan_id: int
    from_node_id: int  # 이 노드가 끝나야
    to_node_id: int  # 이 노드를 시작한다
