"""나누기·합치기·넣기로 새로 생기는 노드 하나. make_plan 의 정의서와 같은 칸이다 (사용자, 2026-11-19)."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.workflow.plan_edit.op.node_output import NodeOutput


@dataclass(frozen=True, slots=True)
class NewPart:
    """나누기·합치기·넣기로 새로 생기는 노드 하나."""

    title: str
    does: str  # 이 노드의 목적과 하는 일 한두 줄
    kind: NodeKind | None = None  # 없으면 나누기는 원래 노드, 합치기는 첫 노드의 종류. 넣기는 꼭 있다
    output: NodeOutput | None = None  # 없으면 형태 "(정하지 않음)"
    notes: str | None = None  # 꼭 할 일과 주의할 점
