"""ask_retry (D 2): 작업 지시를 만들지 못한 노드를 한 질문에 모아 다시 만들지 묻는다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.workflow.plan_run.prompts.retry_choices import RETRY_CHOICES


@TASKS.register_as("plan_run.ask_retry")
class AskRetryTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        failed = context.read("write_prompts")["failed"]
        lines = [f'- 노드 {node["node_id"]} "{node["title"]}": {node["reason"]}' for node in failed]
        question = "\n".join(["아래 노드는 작업 지시를 만들지 못했습니다.", *lines, "다시 만들까요?"])
        return QuestionRequest(question, RETRY_CHOICES)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 선택지 밖의 답이면 같은 질문을 다시 낸다
        if result not in RETRY_CHOICES:
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        return TaskOutput({"answer": result})
