from task_plan_server.exception import ConflictException


class PersonaNameDuplicatedException(ConflictException):
    """같은 이름의 페르소나가 이미 있음 (409). 만들기와 고치기에서 던진다."""

    def __init__(self, name: str) -> None:
        super().__init__(
            f"persona name already exists: {name}",
            client_message=f"이름이 {name} 인 페르소나가 이미 있습니다",
        )
