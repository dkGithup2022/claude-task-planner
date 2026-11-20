from task_plan_server.exception import InvalidInputException


class UnknownPersonaException(InvalidInputException):
    """persona_ids 에 없는(또는 지운) 페르소나가 있음 (400)."""

    def __init__(self, persona_ids: list[int]) -> None:
        joined = ", ".join(str(persona_id) for persona_id in persona_ids)
        super().__init__(
            f"unknown persona ids: {joined}", client_message=f"페르소나 {joined} 가 없습니다"
        )
        self.persona_ids = persona_ids
