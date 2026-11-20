"""ask_failed (D 5): 실패한 노드와 그 이유, 요약, 결과 위치를 보이고 어떻게 할지 묻는다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.model.progress.run_phase import RunPhase
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.plan_run.rounds.failed.failed_choices import FAILED_CHOICES
from task_plan_manager.workflow.plan_run.show_progress import show_waiting_answer


@TASKS.register_as("plan_run.ask_failed")
class AskFailedTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        plan_id = context.read("find_plan")["plan_id"]
        stopped = context.read("run_nodes")
        plan = plan_api_reader().get_plan(plan_id)
        node = plan.node(int(stopped["node_id"]))
        show_waiting_answer(plan, RunPhase.FAILED, node)
        output = DefaultPlanFolderReader().read_output(plan_id, node.node_id)
        lines = [f'노드 {node.node_id} "{node.title}" 이 끝나지 못했습니다.', f"이유: {stopped['detail']['reason']}"]
        if stopped["detail"]["summary"]:
            lines.append(f"요약: {stopped['detail']['summary']}")
        lines += [f"결과: {output.result_path if output else '없음'}", "어떻게 할까요?"]
        return QuestionRequest("\n".join(lines), FAILED_CHOICES)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        if result not in FAILED_CHOICES:
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        return TaskOutput({"answer": result})
