"""자식 실행 방식 하나. ChildRun 값마다 하나."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import ClassVar

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.model.run_state.scenario_node import ScenarioNode
from task_plan_manager.engine.runner.child_run.child_run import ChildRun


class ChildRunStrategy(ABC):
    """자식 실행 방식 하나. ChildRun 값마다 하나."""

    child_run: ClassVar[ChildRun]

    @abstractmethod
    def children_in_turn(self, node: ScenarioNode, context: FlowContext) -> Iterator[tuple[ScenarioNode, str]]:
        """돌릴 차례의 자식과 그 항목 번호(반복 밖이면 NO_ITEM_KEY)를 순서대로 내놓는다."""
