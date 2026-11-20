from .domain_exception import DomainException


class EntityNotFoundException(DomainException):
    """도메인별 하위 클래스(예: ArticleNotFoundException)로만 사용한다. 직접 생성 금지."""

    def __init__(
        self,
        detail: str,
        status_code: int = 404,
        client_message: str = "해당 리소스를 찾을 수 없습니다",
    ) -> None:
        if type(self) is EntityNotFoundException:
            raise TypeError("EntityNotFoundException 은 도메인별 하위 클래스로만 사용한다")
        super().__init__(detail)
        self.http_status_code = status_code
        self.http_error_message = client_message
