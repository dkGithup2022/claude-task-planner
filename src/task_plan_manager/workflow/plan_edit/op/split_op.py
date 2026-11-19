"""노드 하나를 여럿으로 나눈다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.plan_edit.op.new_part import NewPart
from task_plan_manager.workflow.plan_edit.op.split_order import SplitOrder


@dataclass(frozen=True, slots=True)
class SplitOp:
    """노드 하나를 여럿으로 나눈다."""

    node_id: int
    order: SplitOrder
    into: tuple[NewPart, ...]
