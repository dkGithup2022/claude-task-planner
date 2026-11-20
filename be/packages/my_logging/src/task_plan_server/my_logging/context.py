"""로그 컨텍스트. 요청 범위(contextvars)와 프로세스 전역(dict) 두 층.

- 요청 범위: HTTP 요청 1회. 미들웨어가 시작에 set_context, 끝에 clear.
  contextvars 라서 요청마다 독립이고, anyio 가 def 핸들러를 워커 스레드로 넘길 때 복사되어 따라간다.
- 전역: 프로세스 수명. service / version / env 같은 것.
- 같은 키가 양쪽에 있으면 요청 키가 이긴다.
"""

import threading
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

_global: dict[str, Any] = {}
_global_lock = threading.Lock()


def set_context(key: str, value: Any) -> None:
    """요청 범위 키. 같은 키는 덮어쓴다."""
    structlog.contextvars.bind_contextvars(**{key: value})


def remove(key: str) -> None:
    """요청 범위 키 제거. 없어도 조용히 지나간다."""
    structlog.contextvars.unbind_contextvars(key)


def clear() -> None:
    """요청 범위 키 전부 제거. 요청 종료 시 미들웨어가 부른다."""
    structlog.contextvars.clear_contextvars()


def set_global_context(key: str, value: Any) -> None:
    """프로세스 전역 키. 모든 로그 줄에 붙는다."""
    with _global_lock:
        _global[key] = value


def remove_global(key: str) -> None:
    with _global_lock:
        _global.pop(key, None)


def keys() -> tuple[list[str], list[str]]:
    """(전역 키 목록, 요청 범위 키 목록)."""
    with _global_lock:
        g = list(_global)
    return g, list(structlog.contextvars.get_contextvars())


def merge_global_context(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """structlog processor. 전역 키를 합치되 요청 키를 덮어쓰지 않는다."""
    with _global_lock:
        for k, v in _global.items():
            event_dict.setdefault(k, v)
    return event_dict
