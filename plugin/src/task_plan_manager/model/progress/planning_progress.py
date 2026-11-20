"""계획 세우기의 진행. 상태 줄은 "적합한 크기의 계획 세우는 중..." 과 걸린 시간만 보인다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanningProgress:
    started_at: str  # 계획 나누기를 시작한 시각 (ISO 8601 UTC). 걸린 시간을 세는 기준
