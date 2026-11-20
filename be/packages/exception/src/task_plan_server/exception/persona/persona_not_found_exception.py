from task_plan_server.exception import EntityNotFoundException


class PersonaNotFoundException(EntityNotFoundException):
    """기본 404 / "해당 리소스를 찾을 수 없습니다"."""
