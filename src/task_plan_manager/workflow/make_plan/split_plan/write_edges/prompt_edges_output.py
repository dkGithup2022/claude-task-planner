"""간선 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft


@dataclass(frozen=True, slots=True)
class EdgesOutput:
    edges: list[EdgeDraft]  # 산출물이 넘어가는 간선 전부
