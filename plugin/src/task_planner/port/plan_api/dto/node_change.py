"""노드 고치기 요청 (PATCH /plans/{plan_id}/nodes/{node_id}). None 인 필드는 바꾸지 않는다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class NodeChange:
    title: str | None = None
    kind: NodeKind | None = None
    persona_ids: tuple[int, ...] | None = None
    output_spec: str | None = None
    status: PlanNodeStatus | None = None
