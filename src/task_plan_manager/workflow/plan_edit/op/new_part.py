"""나누기·합치기·넣기로 새로 생기는 노드 하나의 내용."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NewPart:
    """나누기·합치기·넣기로 새로 생기는 노드 하나의 내용."""

    title: str
    scope: str  # 하는 일 한두 줄
    output: str | None = None  # 산출물 한 줄 (형태와 담을 것)
    note: str | None = None  # 그 외 설명에 넣을 한 줄
