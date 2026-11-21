"""계획 피드백의 진행. 사용자가 고칠 곳을 말하거나 확정·취소 명령을 고를 차례다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeedbackProgress:
    editing_since: str | None  # 계획을 고치는 중이면 시작 시각. 사용자 차례면 None
