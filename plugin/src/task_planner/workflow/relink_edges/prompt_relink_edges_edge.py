"""간선 다시 정하기 프롬프트 출력의 간선 하나."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelinkEdgesEdge:
    from_id: int  # 앞 노드 id. 이 노드가 끝나야
    to_id: int  # 뒤 노드 id 가 그 산출물을 받아 시작한다
