from .domain_exception import DomainException


class ForbiddenException(DomainException):
    def __init__(
        self,
        detail: str,
        status_code: int = 403,
        client_message: str = "접근 권한이 없습니다",
    ) -> None:
        super().__init__(detail)
        self.http_status_code = status_code
        self.http_error_message = client_message
