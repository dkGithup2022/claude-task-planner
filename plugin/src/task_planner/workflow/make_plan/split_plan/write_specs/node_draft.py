"""저장 전 노드. 노드 spec 필드와, 간선 정리에 쓸 local_id·선행 작업을 함께 담는다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.node_kind import NodeKind
from task_planner.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite


@dataclass(frozen=True, slots=True)
class NodeDraft:
    local_id: str
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]
    output_spec: str  # ### 하는 일 / ### 산출물 / ### 그 외 설명
    path: str  # 트리에서의 경로 ("맨 위 / … / 이 작업"). 간선 정리 입력에 쓴다
    prerequisites: tuple[Prerequisite, ...]
