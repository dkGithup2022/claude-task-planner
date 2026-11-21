"""계획 실행(/plan-run)의 진행. 예: 노드 6번째 / 10개 중, 51 UI 문서 작성 외 1개, 노드를 실행하는 중."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.progress.run_node import RunNode
from task_planner.model.progress.run_phase import RunPhase


@dataclass(frozen=True, slots=True)
class RunProgress:
    phase: RunPhase
    done: int  # 끝난 노드 수 (완료·건너뜀)
    total: int  # 노드 수
    nodes: tuple[RunNode, ...] = ()  # 실행 중인 노드, 또는 확인·실패 처리를 기다리는 노드
