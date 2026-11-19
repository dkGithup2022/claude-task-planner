"""계획 만들기 요청 (POST /plans)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewPlan:
    title: str
    request: str  # 명령서 본문 (md)
    persona_ids: tuple[int, ...]
