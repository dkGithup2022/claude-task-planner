"""관계있는 컨텍스트 고르기 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelevantContextOutput:
    ids: list[int]  # 실제 작업과 관계있는 컨텍스트의 id, 중요한 순서대로. 없으면 빈 목록
