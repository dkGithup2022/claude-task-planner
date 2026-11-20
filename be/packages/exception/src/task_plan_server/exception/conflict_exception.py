from .domain_exception import DomainException


class ConflictException(DomainException):
    def __init__(
        self,
        detail: str,
        status_code: int = 409,
        client_message: str = "이미 존재하는 리소스입니다",
    ) -> None:
        super().__init__(detail)
        self.http_status_code = status_code
        self.http_error_message = client_message
