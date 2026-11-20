from task_plan_server.exception import EntityNotFoundException


class PlanEdgeNotFoundException(EntityNotFoundException):
    """기본 404. 간선 지우기는 없어도 아무것도 하지 않으므로 지금 API 에서는 쓰지 않는다."""
