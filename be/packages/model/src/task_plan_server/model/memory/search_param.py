from dataclasses import dataclass

from .memory_kind import MemoryKind


@dataclass(frozen=True, slots=True)
class SearchParam:
    """지식 검색 조건. 같은 종류이고 페르소나가 하나라도 겹치는 지식을 찾는다."""

    kind: MemoryKind
    query: str
    persona_ids: tuple[int, ...]
    theme: str | None = None  # 주면 이 작업 이름의 지식만
    limit: int = 10
