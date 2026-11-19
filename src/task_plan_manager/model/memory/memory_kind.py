"""지식의 종류."""

from __future__ import annotations

from enum import StrEnum


class MemoryKind(StrEnum):
    """KNOWLEDGE 작업 방법·규칙, ATTITUDE 작업 전체의 판단 방식, PLAN 작업을 나누는 방식."""

    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    PLAN = "plan"
