"""write_edges 의 결과: 정리한 간선과 경고 (버린 간선, 순환 때문에 넣지 않은 간선)."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft


@dataclass(frozen=True, slots=True)
class EdgesResult:
    edges: tuple[EdgeDraft, ...]
    warnings: tuple[str, ...]
