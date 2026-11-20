"""HTTP 요청 1회 = 로그 컨텍스트 1회.

순수 ASGI 미들웨어. 시작에 request_id / method / path 를 바인딩하고,
끝에 status / duration_ms 한 줄을 남기고 clear 한다.
send 를 감싸 http.response.start 에서 상태 코드를 잡는다.
잡히지 않은 예외는 500 으로 기록하고 재전파한다 (응답은 바깥 ServerErrorMiddleware 가 만든다).
"""

import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from task_plan_server.my_logging import clear, get_logger, set_context

Receive = Callable[[], Awaitable[Any]]
Send = Callable[[Any], Awaitable[None]]
ASGIApp = Callable[[dict[str, Any], Receive, Send], Awaitable[None]]

REQUEST_ID_HEADER = b"x-request-id"


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        request_id = headers.get(REQUEST_ID_HEADER, b"").decode() or uuid.uuid4().hex[:16]
        method, path = scope["method"], scope["path"]

        clear()
        set_context("request_id", request_id)
        set_context("method", method)
        set_context("path", path)

        status: dict[str, int | None] = {"code": None}
        started = time.perf_counter()

        async def send_wrapped(message: Any) -> None:
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
                out = list(message.get("headers", []))
                out.append((REQUEST_ID_HEADER, request_id.encode()))
                message["headers"] = out
            await send(message)

        try:
            await self.app(scope, receive, send_wrapped)
        except Exception:
            status["code"] = 500
            raise
        finally:
            code = status["code"] or 500
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            log = get_logger("http")
            emit = log.error if code >= 500 else log.info
            emit("http.request", status=code, duration_ms=duration_ms)
            clear()
