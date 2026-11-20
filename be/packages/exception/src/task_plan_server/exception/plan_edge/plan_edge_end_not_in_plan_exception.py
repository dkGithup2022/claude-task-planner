from task_plan_server.exception import InvalidInputException


class PlanEdgeEndNotInPlanException(InvalidInputException):
    """간선의 앞이나 뒤 노드가 그 계획에 없음 (400)."""

    def __init__(self, plan_id: int, node_id: int) -> None:
        super().__init__(
            f"node {node_id} is not in plan {plan_id}",
            client_message=f"노드 {node_id} 가 계획 {plan_id} 에 없습니다",
        )
        self.plan_id = plan_id
        self.node_id = node_id
