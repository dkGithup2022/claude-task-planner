"""Plan ↔ JSON. 모양은 데이터·API 문서의 GET /plans/{plan_id} 응답이고, mock 파일도 같은 모양으로 저장한다."""

from __future__ import annotations

from typing import Any

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus


class PlanJsonConverter:
    def to_body(self, plan: Plan) -> dict[str, Any]:
        return {
            "plan_id": plan.plan_id,
            "title": plan.title,
            "request": plan.request,
            "persona_ids": list(plan.persona_ids),
            "status": plan.status.value,
            "created_at": plan.created_at,
            "nodes": [_node_to_file(node) for node in plan.nodes],
            "edges": [_edge_to_file(edge) for edge in plan.edges],
        }

    def to_plan(self, plan_json: dict[str, Any]) -> Plan:
        return Plan(
            plan_id=int(plan_json["plan_id"]),
            title=plan_json["title"],
            request=plan_json["request"],
            persona_ids=tuple(int(persona_id) for persona_id in plan_json["persona_ids"]),
            status=PlanStatus(plan_json["status"]),
            created_at=plan_json["created_at"],
            nodes=tuple(_node_to_data(node_json) for node_json in plan_json["nodes"]),
            edges=tuple(_edge_to_data(edge_json) for edge_json in plan_json["edges"]),
        )


def _node_to_file(node: PlanNode) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "title": node.title,
        "kind": node.kind.value,
        "persona_ids": list(node.persona_ids),
        "output_spec": node.output_spec,
        "status": node.status.value,
    }


def _node_to_data(node_json: dict[str, Any]) -> PlanNode:
    return PlanNode(
        node_id=int(node_json["node_id"]),
        title=node_json["title"],
        kind=NodeKind(node_json["kind"]),
        persona_ids=tuple(int(persona_id) for persona_id in node_json["persona_ids"]),
        output_spec=node_json["output_spec"],
        status=PlanNodeStatus(node_json["status"]),
    )


def _edge_to_file(edge: PlanEdge) -> dict[str, Any]:
    return {"edge_id": edge.edge_id, "from_node_id": edge.from_node_id, "to_node_id": edge.to_node_id}


def _edge_to_data(edge_json: dict[str, Any]) -> PlanEdge:
    return PlanEdge(
        edge_id=int(edge_json["edge_id"]),
        from_node_id=int(edge_json["from_node_id"]),
        to_node_id=int(edge_json["to_node_id"]),
    )
