"""도구를 쓰는 claude -p 한 번의 결과."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AgentResult:
    text: str  # 답 글 전문 (claude -p 의 result)
    cost_usd: float
    seconds: float  # 걸린 시간
