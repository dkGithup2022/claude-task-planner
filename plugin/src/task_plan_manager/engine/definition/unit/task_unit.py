"""작업 하나와 그 수행자."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.unit import Unit
from task_plan_manager.engine.performer.performed_by import PerformedBy


@dataclass(frozen=True, slots=True, kw_only=True)
class TaskUnit(Unit):
    """작업 하나와 그 수행자."""

    performed_by: PerformedBy
    task: Ref  # TASKS 의 키와 인자

    def check(self) -> None:
        if not isinstance(self.task, Ref):
            raise ValueError(f"{self.name}: task 는 Ref 여야 한다")
