"""노드 저장 요청 (POST /plans/{plan_id}/nodes). id 와 상태는 저장소가 정한다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.plan.node_kind import NodeKind


@dataclass(frozen=True, slots=True)
class NewNode:
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]
    output_spec: str
