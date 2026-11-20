from .domain_exception import DomainException


class UnauthorizedException(DomainException):
    def __init__(
        self,
        detail: str,
        status_code: int = 401,
        client_message: str = "인증이 필요합니다",
    ) -> None:
        super().__init__(detail)
        self.http_status_code = status_code
        self.http_error_message = client_message
