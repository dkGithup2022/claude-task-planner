"""write_request 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WriteRequestOutput:
    title: str  # 명령을 한 줄로. 계획 이름
    request: str  # 명령서 md (명령, 맥락, 할 일, 중요한 것, 산출물, 범위 밖, 저장소, 종류)
