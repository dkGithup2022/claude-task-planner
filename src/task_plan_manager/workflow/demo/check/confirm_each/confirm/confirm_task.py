"""check/confirm_each/confirm: 반복 항목(과일) 하나마다 맞는지 묻는다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.workflow.demo.check.choose_task import ChooseTask


@TASKS.register_as("demo.confirm")
class ConfirmTask(ChooseTask):
    choices = ("맞음", "아님")

    def build_request(self, context: FlowContext) -> QuestionRequest:
        return QuestionRequest(f"{context.current_item()} 맞나요?", self.choices)
