from dataclasses import dataclass

from fastapi import Request

from task_plan_server.exception import UnauthorizedException

DEV_USER_HEADER = "X-User-Id"


@dataclass(frozen=True, slots=True)
class CurrentUser:
    user_id: int


def resolve_current_user(request: Request, env: str) -> CurrentUser:
    """개발용 stub. env == "local" 에서만 X-User-Id 헤더를 믿는다.

    그 외 환경에서는 무조건 401 — 헤더 신뢰가 프로덕션에 남는 것을 막는 가드.
    실제 인증은 별도 스킬이 이 함수와 RequestProvider.current_user 를 교체한다.
    """
    if env != "local":
        raise UnauthorizedException("authentication is not configured for this environment")
    raw = request.headers.get(DEV_USER_HEADER)
    if raw is None or not raw.isdigit():
        raise UnauthorizedException(f"missing or invalid {DEV_USER_HEADER} header")
    return CurrentUser(user_id=int(raw))
