from enum import StrEnum


class NodeKind(StrEnum):
    """노드가 하는 일의 종류. HITL 은 사용자 확인 노드. 값은 CLI 와 같은 소문자다."""

    DOCUMENT = "document"
    RESEARCH = "research"
    CODE = "code"
    HITL = "hitl"
