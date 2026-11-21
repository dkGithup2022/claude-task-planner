"""ask_rerun (D 1-1): 결과 파일 없이 끊긴 노드를 한 질문에 모아 다시 실행할지 묻는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.workflow.plan_run.resume.rerun_choices import RERUN_CHOICES


@TASKS.register_as("plan_run.ask_rerun")
class AskRerunTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        nodes = context.read("check_broken")["nodes"]
        lines = [f'- 노드 {node["node_id"]} "{node["title"]}"' for node in nodes]
        question = "\n".join(["아래 노드는 실행 중에 끊겼고 결과 파일이 없습니다.", *lines, "다시 실행할까요?"])
        return QuestionRequest(question, RERUN_CHOICES)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 선택지 밖의 답이면 같은 질문을 다시 낸다
        if result not in RERUN_CHOICES:
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        return TaskOutput({"answer": result})
