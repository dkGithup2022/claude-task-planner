"""노드 여럿을 하나로 합친다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.plan_edit.op.new_part import NewPart


@dataclass(frozen=True, slots=True)
class MergeOp:
    """노드 여럿을 하나로 합친다."""

    node_ids: tuple[int, ...]
    part: NewPart
