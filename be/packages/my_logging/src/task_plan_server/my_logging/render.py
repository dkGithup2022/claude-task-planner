"""렌더러.

json 은 유효한 한 줄 JSON. json-color 는 같은 모양에 ANSI 색 (터미널 전용, 유효 JSON 아님).
"""

import json
from typing import Any

from structlog.typing import EventDict, WrappedLogger

_FIRST = ("timestamp", "level", "logger", "event")
_RESET = "\033[0m"
_KEY = "\033[36m"  # cyan
_LEVEL = {
    "debug": "\033[2m",  # dim
    "info": "\033[32m",  # green
    "warning": "\033[33m",  # yellow
    "error": "\033[31m",  # red
    "critical": "\033[35m",  # magenta
}


def order_keys(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    """timestamp, level, logger, event 를 앞으로. 나머지는 삽입 순서."""
    ordered: EventDict = {k: event_dict[k] for k in _FIRST if k in event_dict}
    for k, v in event_dict.items():
        ordered.setdefault(k, v)
    return ordered


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


class ColorJSONRenderer:
    """한 줄 JSON 모양. 키는 cyan, level 값은 심각도 색."""

    def __call__(self, _: WrappedLogger, __: str, event_dict: EventDict) -> str:
        parts = []
        for k, v in event_dict.items():
            val = _dump(v)
            if k == "level":
                val = f"{_LEVEL.get(str(v), '')}{val}{_RESET}"
            parts.append(f'{_KEY}"{k}"{_RESET}:{val}')
        return "{" + ",".join(parts) + "}"
