from typing import Protocol


class HttpException(Protocol):
    """HTTP 로 노출될 예외가 갖는 속성. error_handlers 가 이 두 값을 그대로 쓴다."""

    http_status_code: int
    http_error_message: str
