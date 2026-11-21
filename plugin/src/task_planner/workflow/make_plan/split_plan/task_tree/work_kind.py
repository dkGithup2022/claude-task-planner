"""작업 트리의 작업 종류. 값은 나누기 프롬프트가 쓰는 글자 그대로."""

from __future__ import annotations

from enum import StrEnum


class WorkKind(StrEnum):
    """보통 작업이면 TASK, 사용자가 앞 결과를 확인하고 허가하는 자리면 HITL."""

    TASK = "작업"
    HITL = "HITL"
