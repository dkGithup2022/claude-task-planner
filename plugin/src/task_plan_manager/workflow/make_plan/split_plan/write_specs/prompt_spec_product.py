"""정의서 출력의 output (산출물)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SpecProduct:
    form: str  # 문서 / 표 / 결정 / 코드 변경 / 조사 노트
    contents: str  # 담을 것 2~4줄. 코드면 저장소 경로와 주요 작업 내용
