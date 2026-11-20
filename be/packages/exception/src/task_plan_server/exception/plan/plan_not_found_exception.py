from task_plan_server.exception import EntityNotFoundException


class PlanNotFoundException(EntityNotFoundException):
    """기본 404. CLI 는 404 를 PlanNotFoundError 로 바꿔 읽는다."""
