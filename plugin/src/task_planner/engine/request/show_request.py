"""MAIN_SESSION_SHOW 가 받음 → 결과 없음 (보이자마자 끝)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShowRequest:
    """MAIN_SESSION_SHOW 가 받음 → 결과 없음 (보이자마자 끝)."""

    text: str
    skill: str | None = None  # 보인 뒤 메인 세션이 이어서 부를 스킬 (예: "task-planner:plan-feedback 6")
