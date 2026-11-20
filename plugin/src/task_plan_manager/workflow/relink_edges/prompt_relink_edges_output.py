"""간선 다시 정하기 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.relink_edges.prompt_relink_edges_edge import RelinkEdgesEdge


@dataclass(frozen=True, slots=True)
class RelinkEdgesOutput:
    edges: list[RelinkEdgesEdge]  # 바뀐 노드와 앞뒤 노드 사이의 간선 전부
