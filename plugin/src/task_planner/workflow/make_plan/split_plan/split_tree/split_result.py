"""split_tree 의 결과: 다 나눈 작업 트리와, 상한 때문에 멈춘 일 같은 경고."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.task_tree.task_tree import TaskTree


@dataclass(frozen=True, slots=True)
class SplitResult:
    tree: TaskTree  # 맨 아래 작업에 local_id 가 붙어 있다
    warnings: tuple[str, ...]
