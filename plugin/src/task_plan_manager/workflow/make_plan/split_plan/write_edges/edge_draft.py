"""저장 전 간선. 양 끝을 작업의 local_id 로 가리킨다. 저장할 때 서버 id 로 바뀐다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EdgeDraft:
    from_local_id: str  # 앞 작업. 이 작업이 끝나야
    to_local_id: str  # 뒤 작업이 그 산출물을 받아 시작한다
