"""ask_confirm (D 4): 확인 노드에서 다음으로 넘어가도 되는지 묻는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.workflow.plan_run.rounds.confirm.confirm_choices import CONFIRM_CHOICES


@TASKS.register_as("plan_run.ask_confirm")
class AskConfirmTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        plan = plan_api_reader().get_plan(context.read("find_plan")["plan_id"])
        node = plan.node(int(context.read("run_nodes")["node_id"]))
        return QuestionRequest(f'노드 {node.node_id} "{node.title}": 다음으로 넘어가도 될까요?', CONFIRM_CHOICES)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        if result not in CONFIRM_CHOICES:
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        return TaskOutput({"answer": result})
