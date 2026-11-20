from task_plan_server.exception import ConflictException


class PersonaInUseException(ConflictException):
    """이 페르소나를 쓰는 지식이나 계획이 있어 지울 수 없음 (409). 웹이 메시지를 그대로 보인다."""

    def __init__(self, persona_id: int, memory_count: int, plan_count: int) -> None:
        super().__init__(
            f"persona {persona_id} is used by {memory_count} memories, {plan_count} plans",
            client_message=f"지식 {memory_count}개, 계획 {plan_count}개가 이 페르소나를 씁니다",
        )
        self.memory_count = memory_count
        self.plan_count = plan_count
