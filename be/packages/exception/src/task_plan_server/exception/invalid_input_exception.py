from .domain_exception import DomainException


class InvalidInputException(DomainException):
    def __init__(
        self,
        detail: str,
        status_code: int = 400,
        client_message: str = "잘못된 요청입니다",
    ) -> None:
        super().__init__(detail)
        self.http_status_code = status_code
        self.http_error_message = client_message
