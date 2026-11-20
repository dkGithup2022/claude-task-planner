"""상태 줄에 이름이 오르는 노드 하나. 실행 중인 노드, 또는 확인·실패 처리를 기다리는 노드."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunNode:
    node_id: int
    title: str
    started_at: str | None  # 실행 중이면 시작 시각. 걸린 시간을 세는 기준
