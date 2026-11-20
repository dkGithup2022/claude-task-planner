"""계획 노드의 종류."""

from __future__ import annotations

from enum import StrEnum


class NodeKind(StrEnum):
    """노드가 하는 일의 종류. 예: 조사 노드는 RESEARCH, 사용자 확인 노드는 HITL."""

    DOCUMENT = "document"
    RESEARCH = "research"
    CODE = "code"
    HITL = "hitl"
