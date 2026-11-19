"""노드 하나를 여럿으로 나눈다. 나뉜 노드 사이와 앞뒤의 간선은 간선 다시 정하기가 정한다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.plan_edit.op.new_part import NewPart


@dataclass(frozen=True, slots=True)
class SplitOp:
    """노드 하나를 여럿으로 나눈다."""

    node_id: int
    into: tuple[NewPart, ...]
