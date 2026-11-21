"""본문 쓰기 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WriteKnowledgeOutput:
    theme: str  # 작업 이름. 덧붙이기면 기존 지식의 작업 이름
    body: str  # md 줄글. 설명과 예시 3~4개. 덧붙이기면 더할 내용만
