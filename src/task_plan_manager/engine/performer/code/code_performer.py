"""CodePerformer: 코드가 바로 수행한다 (일은 작업의 build_output 이 함)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.model.run_state.scenario_node import ScenarioNode
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.performer.task_performer import TaskPerformer
from task_plan_manager.engine.request.task_request import TaskRequest


class CodePerformer(TaskPerformer):
    performed_by = PerformedBy.CODE

    def perform(self, node: ScenarioNode, request: TaskRequest, context: FlowContext) -> Any:
        return None  # 일은 build_output 이 한다
