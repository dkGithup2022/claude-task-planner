"""find_plan: 명령 줄에서 계획 id 를 읽고, 실행할 수 있는 계획인지 확인하고, 뒤 단계가 쓸 값을 남긴다.
뒤 단계가 쓰는 값: 계획 id, 제목, 지금 상태 (start_run 이 승인인지 실행 중인지 본다)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.port.plan_api.plan_not_found_error import PlanNotFoundError
from task_plan_manager.workflow.plan_run.find_plan.command_plan_id import command_plan_id
from task_plan_manager.workflow.plan_run.find_plan.current_transcript import current_transcript
from task_plan_manager.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError
from task_plan_manager.workflow.plan_run.find_plan.runnable_check import require_runnable


@TASKS.register_as("plan_run.find_plan")
class FindPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 읽기: 명령 줄의 id → 계획 저장소의 계획 → 이 작업 폴더의 계획 폴더
        plan_id = command_plan_id(current_transcript(context))
        plan = _stored_plan(plan_id)
        _require_plan_folder(plan_id)
        # 판정: 승인·실행 중만 실행한다
        require_runnable(plan)
        return TaskOutput({"plan_id": plan_id, "title": plan.title, "status": plan.status.value})


def _stored_plan(plan_id: int) -> Plan:
    """계획 저장소의 계획. 없으면 PlanNotRunnableError."""
    try:
        return plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as missing:
        raise PlanNotRunnableError(f"계획 {plan_id} 이 계획 저장소에 없습니다") from missing


def _require_plan_folder(plan_id: int) -> None:
    """작업 지시와 결과를 둘 계획 폴더가 이 작업 폴더에 있어야 한다. 없으면 PlanNotRunnableError."""
    if plan_id not in DefaultPlanFolderReader().list_plan_ids():
        raise PlanNotRunnableError(
            f"계획 {plan_id} 의 계획 폴더가 이 작업 폴더에 없습니다. 계획을 만든 폴더에서 불러 주세요"
        )
