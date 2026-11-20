"""configure_logging — 표준 logging 루트 핸들러에 structlog 포매터를 건다.

그래서 logging.getLogger(__name__) 로 찍는 기존 코드, uvicorn 로거, structlog 로거가
전부 같은 형식으로 나간다.
uvicorn 의 액세스 로그는 끈다 (app 의 RequestLoggingMiddleware 가 대체).
"""

import json
import logging
import sys
from typing import Literal

import structlog

from .context import merge_global_context
from .render import ColorJSONRenderer, order_keys

LogFormat = Literal["json", "json-color", "console"]


def configure_logging(level: str = "INFO", fmt: LogFormat = "json") -> None:
    shared: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,  # 요청 범위 키
        merge_global_context,  # 전역 키 (요청 키를 덮지 않음)
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,  # exc_info -> "exception" 문자열
        order_keys,
    ]

    renderer: structlog.typing.Processor
    if fmt == "json":
        renderer = structlog.processors.JSONRenderer(
            serializer=json.dumps, ensure_ascii=False, separators=(",", ":"), default=str
        )
    elif fmt == "json-color":
        renderer = ColorJSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,  # 표준 logging 으로 들어온 레코드에도 같은 체인
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    for name in ("uvicorn", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
    logging.getLogger("uvicorn.access").disabled = True
