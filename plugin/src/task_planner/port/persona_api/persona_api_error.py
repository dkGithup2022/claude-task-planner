"""페르소나 목록을 서버에서 읽지 못함."""

from __future__ import annotations


class PersonaApiError(RuntimeError):
    """메시지에 부른 주소와 서버 응답을 담는다."""
