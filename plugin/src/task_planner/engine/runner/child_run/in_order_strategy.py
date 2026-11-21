"""InOrderStrategy: 자식을 차례로 돌린다."""

from __future__ import annotations

from collections.abc import Iterator

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.model.result.item_key import NO_ITEM_KEY
from task_planner.engine.model.run_state.scenario_node import ScenarioNode
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.engine.runner.child_run.child_run_strategy import ChildRunStrategy


class InOrderStrategy(ChildRunStrategy):
    child_run = ChildRun.IN_ORDER

    def children_in_turn(self, node: ScenarioNode, context: FlowContext) -> Iterator[tuple[ScenarioNode, str]]:
        for child in node.children:
            yield child, context.item_key or NO_ITEM_KEY
