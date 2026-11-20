"""노드 하나를 실행한 결과. 작업 스레드가 만들고, 부르는 스레드가 기록한다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class NodeOutcome:
    node_id: int
    status: PlanNodeStatus  # DONE | FAILED
    reason: str  # 실패 이유. 완료면 ""
    summary: str  # 답의 둘째 줄부터 (세 줄 이내 요약)
    cost_usd: float = 0.0
    seconds: float = 0.0
