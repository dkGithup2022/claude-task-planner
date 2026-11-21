"""계획의 진행 상태. 끝 판정과 알림의 노드별 상태 표가 같이 쓴다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanProgress:
    counts: dict[PlanNodeStatus, int]  # 상태마다 노드 수
    finished: bool  # 모든 노드가 완료·건너뜀
    blocked: bool  # 안 끝났는데 실행할 노드, 확인 노드, 실행 중인 노드, 실패한 노드가 모두 없음
