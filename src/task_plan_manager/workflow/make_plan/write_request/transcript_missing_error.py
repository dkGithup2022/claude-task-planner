"""interview 결과에 대화 기록 경로가 없음. 세션 시작 훅이 돌지 않은 세션이다."""

from __future__ import annotations


class TranscriptMissingError(RuntimeError):
    """대화 없이는 명령서를 쓸 수 없어 이 단계를 실패로 멈춘다 (사용자, 2026-11-19)."""
