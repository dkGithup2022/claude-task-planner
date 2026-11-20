from task_plan_server.exception import EntityNotFoundException


class PlanNodeNotFoundException(EntityNotFoundException):
    """기본 404. 다른 계획의 노드 id 를 보내도 없음으로 본다."""
