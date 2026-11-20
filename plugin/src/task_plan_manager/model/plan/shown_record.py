"""계획을 사용자에게 보여 준 기록. B 의 지식 추출이 이 시각 뒤의 대화를 그 대화 기록 파일에서 읽는다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShownRecord:
    shown_at: str  # 보여 준 시각 (ISO 8601 UTC)
    transcript: str | None  # 보여 준 대화의 기록 파일 경로. 세션 시작 훅이 돌지 않았으면 None
