"""노드가 한 회차에 읽은 선행 노드 결과 하나."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadInput:
    node_id: int
    round: int  # 읽은 선행 노드 결과의 회차
