"""정의서 출력의 needs 항목 하나."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpecNeed:
    what: str  # 필요한 정보
    source: str  # 출처: 트리의 다른 작업 이름, "명령서", "저장소" 중 하나. 원문의 from (파이썬 예약어라 이름을 바꿈)
