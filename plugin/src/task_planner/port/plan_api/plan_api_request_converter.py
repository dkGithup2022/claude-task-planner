"""계획 저장소 서버 API 의 요청 본문과, 응답에서 id 를 꺼내는 일."""

from __future__ import annotations

from typing import Any

from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.dto.node_change import NodeChange


class PlanApiRequestConverter:
    def to_new_plan_body(self, new_plan: NewPlan) -> dict[str, Any]:
        return {"title": new_plan.title, "request": new_plan.request, "persona_ids": list(new_plan.persona_ids)}

    def to_new_node_body(self, new_node: NewNode) -> dict[str, Any]:
        return {
            "title": new_node.title,
            "kind": new_node.kind.value,
            "persona_ids": list(new_node.persona_ids),
            "output_spec": new_node.output_spec,
        }

    def to_node_change_body(self, change: NodeChange) -> dict[str, Any]:
        """값이 있는 필드만 보낸다 (PATCH)."""
        body: dict[str, Any] = {
            "title": change.title,
            "kind": change.kind.value if change.kind else None,
            "persona_ids": list(change.persona_ids) if change.persona_ids is not None else None,
            "output_spec": change.output_spec,
            "status": change.status.value if change.status else None,
        }
        return {field: value for field, value in body.items() if value is not None}

    def to_status_body(self, status: PlanStatus) -> dict[str, Any]:
        return {"status": status.value}

    def to_id(self, body: dict[str, Any], field: str) -> int:
        """응답에서 plan_id, node_id, edge_id 같은 id 하나."""
        return int(body[field])
