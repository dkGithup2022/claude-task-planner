"""지식 추출 프롬프트가 낸 후보 하나. 저장 전이다. C 가 다듬어 저장한다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeCandidate:
    type: str  # plan(일을 나누는 방식) | domain(그 일을 하는 방법·규칙·사실)
    theme: str  # 이 지식을 꺼내 쓸 작업 이름. "{대상} {행위}"
    content: str  # 맥락 없이도 이해되는 "어떤 일을 어떻게 한다"
    quotes: list[str]  # 근거가 된 사용자 말, 글자 그대로
