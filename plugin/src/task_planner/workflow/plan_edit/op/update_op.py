"""노드의 값 일부를 바꾼다. None 인 값은 그대로 둔다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.plan.node_kind import NodeKind
from task_planner.workflow.plan_edit.op.node_output import NodeOutput


@dataclass(frozen=True, slots=True)
class UpdateOp:
    """노드의 값 일부를 바꾼다. None 인 값은 그대로 둔다."""

    node_id: int
    title: str | None = None
    does: str | None = None  # "하는 일" 절을 바꾼다
    kind: NodeKind | None = None
    persona_ids: tuple[int, ...] | None = None
    output: NodeOutput | None = None  # "산출물" 절을 바꾼다
    add_note: str | None = None  # "그 외 설명" 끝에 한 줄을 더한다
