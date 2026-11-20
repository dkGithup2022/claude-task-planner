from dataclasses import dataclass

from .memory_kind import MemoryKind


@dataclass(frozen=True, slots=True)
class MemoryListCondition:
    """웹 지식 목록의 조건. 비운 조건은 거르지 않는다."""

    query: str = ""  # 작업 이름이나 본문에 들어 있는 글자
    kind: MemoryKind | None = None
    persona_id: int | None = None
    limit: int | None = None  # None 이면 전부
