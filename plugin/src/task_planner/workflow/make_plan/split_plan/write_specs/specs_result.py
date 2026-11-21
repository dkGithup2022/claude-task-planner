"""write_specs 의 결과: 맨 아래 작업마다의 저장 전 노드와 경고."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft


@dataclass(frozen=True, slots=True)
class SpecsResult:
    drafts: tuple[NodeDraft, ...]  # 트리 순서 (n1, n2 …)
    warnings: tuple[str, ...]
