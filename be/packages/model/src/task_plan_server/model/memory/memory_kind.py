from enum import StrEnum


class MemoryKind(StrEnum):
    """KNOWLEDGE 작업 방법·규칙, ATTITUDE 작업 전체의 판단 방식, PLAN 작업을 나누는 방식.

    값은 CLI 가 보내고 읽는 소문자를 그대로 쓴다.
    """

    KNOWLEDGE = "knowledge"
    ATTITUDE = "attitude"
    PLAN = "plan"
