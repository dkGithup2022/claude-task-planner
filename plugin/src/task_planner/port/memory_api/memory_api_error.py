"""지식을 읽거나 쓰지 못함."""

from __future__ import annotations


class MemoryApiError(RuntimeError):
    """메시지에 요청과 이유를 담는다. 예: 덧붙일 지식이 없음, 서버 실패."""
