"""새 노드나 고치는 노드의 산출물: 형태와 담을 것 (make_plan 정의서의 output 과 같은 칸)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NodeOutput:
    form: str  # 문서 / 표 / 결정 / 코드 변경 / 조사 노트
    contents: str = ""  # 담을 것 2~4줄
