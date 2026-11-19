"""두 노드 사이(또는 한쪽 끝)에 노드를 넣는다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.workflow.plan_edit.op.new_part import NewPart


@dataclass(frozen=True, slots=True)
class InsertOp:
    """두 노드 사이(또는 한쪽 끝)에 노드를 넣는다."""

    after: int | None  # 이 노드의 산출물을 받는다
    before: int | None  # 이 노드가 새 노드의 산출물을 받는다
    kind: NodeKind
    part: NewPart
