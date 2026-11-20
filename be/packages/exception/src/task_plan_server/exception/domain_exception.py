class DomainException(Exception):
    """모든 도메인 예외의 부모. detail 은 로그용 내부 메시지."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail
