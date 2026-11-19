"""최종 본문 정하기 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FinalizeKnowledgeOutput:
    save: bool  # 사용자가 저장하자고 했으면 true
    theme: str  # 작업 이름
    body: str  # 사용자가 마지막으로 확인한 본문
