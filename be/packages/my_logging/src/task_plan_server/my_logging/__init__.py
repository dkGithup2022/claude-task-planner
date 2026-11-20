"""my_logging — 로그 형식과 컨텍스트를 한 곳에서.

도메인 코드는 logging.getLogger(__name__) 를 그대로 써도 같은 형식으로 나간다.
요청 컨텍스트에 키를 더할 때만 set_context 를 쓴다.
"""

from typing import Any

import structlog

from .config import LogFormat, configure_logging
from .context import (
    clear,
    keys,
    remove,
    remove_global,
    set_context,
    set_global_context,
)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.stdlib.get_logger(name)


def log(message: str, **fields: Any) -> None:
    """일반 출력. print 대신 이걸 쓴다. level 은 info."""
    get_logger().info(message, **fields)


def info(message: str, **fields: Any) -> None:
    get_logger().info(message, **fields)


def warning(message: str, **fields: Any) -> None:
    get_logger().warning(message, **fields)


def error(message: str, **fields: Any) -> None:
    get_logger().error(message, **fields)


__all__ = [
    "LogFormat",
    "clear",
    "configure_logging",
    "error",
    "get_logger",
    "info",
    "keys",
    "log",
    "remove",
    "remove_global",
    "set_context",
    "set_global_context",
    "warning",
]
