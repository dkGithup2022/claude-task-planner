"""나누기 프롬프트 출력의 children 항목 하나."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SplitChild:
    name: str  # 작업 이름. "{대상} {행위}"
    kind: str  # "작업" 또는 "HITL"
    scope: str  # 목적 한 줄. HITL 이면 확인받을 것
    source: str  # "일반적인 분해" 또는 "검색 결과: <어느 기록>". 원문의 from (파이썬 예약어라 이름을 바꿈)
