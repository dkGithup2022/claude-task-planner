from dataclasses import dataclass

from .memory_kind import MemoryKind


@dataclass(frozen=True, slots=True)
class MemorySearchHit:
    """검색 결과 한 줄. 점수가 높을수록 검색어와 가깝다."""

    memory_id: int
    kind: MemoryKind
    theme: str
    body: str
    score: float
