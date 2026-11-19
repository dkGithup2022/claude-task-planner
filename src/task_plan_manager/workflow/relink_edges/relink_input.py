"""간선 다시 정하기 프롬프트의 입력 JSON 을 만든다. 칸 이름은 프롬프트의 입력 절과 같다."""

from __future__ import annotations

import json
from typing import Any

from task_plan_manager.model.plan.node_spec import NodeSpec
from task_plan_manager.workflow.relink_edges.relink_node import RelinkNode
from task_plan_manager.workflow.relink_edges.relink_request import Edge, RelinkRequest


def build_relink_input(request: RelinkRequest) -> str:
    data = {
        "change": request.change,
        "original_nodes": [_node(node) for node in request.original_nodes],
        "changed_nodes": [_node(node) for node in request.changed_nodes],
        "neighbor_nodes": [_node(node) for node in request.neighbor_nodes],
        "previous_edges": _edges(request.previous_edges),
        "user_edges": {"link": _edges(request.user_links), "unlink": _edges(request.user_unlinks)},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def _node(node: RelinkNode) -> dict[str, Any]:
    """노드 하나: 정의서 md 를 하는 일, 산출물(형태, 담을 것), 그 외 설명으로 나눈다."""
    spec = NodeSpec.from_md(node.output_spec)
    return {
        "id": node.node_id,
        "title": node.title,
        "kind": node.kind,
        "does": spec.does,
        "output": {"form": spec.output_form, "contents": spec.output_contents},
        "notes": spec.notes,
    }


def _edges(edges: tuple[Edge, ...]) -> list[dict[str, int]]:
    return [{"from": from_id, "to": to_id} for from_id, to_id in sorted(edges)]
