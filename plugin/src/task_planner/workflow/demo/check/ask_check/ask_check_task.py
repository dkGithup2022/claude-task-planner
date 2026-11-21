"""check/ask_check: 과일마다 확인할지 묻는다. 답이 "예"면 confirm_each 가 실행된다."""

from __future__ import annotations

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.workflow.demo.check.choose_task import ChooseTask


@TASKS.register_as("demo.ask_check")
class AskCheckTask(ChooseTask):
    choices = ("예", "아니요")

    def build_request(self, context: FlowContext) -> QuestionRequest:
        return QuestionRequest("과일마다 확인할까요?", self.choices)
