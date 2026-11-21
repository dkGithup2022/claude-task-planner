"""계획의 노드 하나."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanNode:
    node_id: int
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]  # 개입하는 페르소나 id. 확인 노드(HITL)면 빈 튜플
    output_spec: str  # md. ### 하는 일, ### 산출물, ### 그 외 설명
    status: PlanNodeStatus
