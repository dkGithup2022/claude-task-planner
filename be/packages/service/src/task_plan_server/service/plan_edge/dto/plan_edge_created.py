from dataclasses import dataclass

from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead


@dataclass(frozen=True, slots=True)
class PlanEdgeCreated:
    """간선 저장 결과. 같은 간선이 이미 있으면 created 는 False 이고 그 간선을 담는다."""

    edge: PlanEdgeRead
    created: bool
