"""두 노드 사이(또는 한쪽 끝)에 노드를 넣는다. after, before 는 자리 표시이고, 간선은 간선 다시 정하기가 정한다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.plan_edit.op.new_part import NewPart


@dataclass(frozen=True, slots=True)
class InsertOp:
    """두 노드 사이(또는 한쪽 끝)에 노드를 넣는다. 새 노드의 kind 는 꼭 있다."""

    after: int | None  # 새 노드 앞에 오는 노드
    before: int | None  # 새 노드 뒤에 오는 노드
    part: NewPart
