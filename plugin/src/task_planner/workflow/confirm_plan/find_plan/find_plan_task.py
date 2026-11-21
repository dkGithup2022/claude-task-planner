"""find_plan: 명령 줄에서 계획 id 를 읽고, 확정할 수 있는 계획인지 확인하고, 뒤 단계가 쓸 값을 남긴다.
뒤 단계가 쓰는 값: 계획 id, 제목, 참여 페르소나, 계획을 보여 준 시각과 그 대화의 기록 파일 (지식 추출이 읽는다)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.port.session.default_session_reader import DefaultSessionReader
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.model.plan.shown_record import ShownRecord
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError
from task_planner.workflow.confirm_plan.find_plan.command_plan_id import command_plan_id
from task_planner.workflow.confirm_plan.find_plan.plan_not_confirmable_error import PlanNotConfirmableError
from task_planner.workflow.list_plans.show_plans.plan_status_label import status_label


@TASKS.register_as("confirm_plan.find_plan")
class FindPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 명령 줄에서 계획 id 를 읽고, 검토 중인지와 보여 준 기록을 확인해 뒤 단계가 쓸 값을 남긴다
        plan_id = command_plan_id(_current_transcript(context))
        plan = _reviewing_plan(plan_id)
        shown = _shown_record(plan_id)
        return TaskOutput(
            {
                "plan_id": plan_id,
                "title": plan.title,
                "persona_ids": list(plan.persona_ids),
                "shown_at": shown.shown_at,
                "transcript": shown.transcript,
            }
        )


def _current_transcript(context: FlowContext) -> Path:
    """지금 대화의 기록 파일. 세션 시작 훅이 session.json 에 남긴 경로."""
    session = DefaultSessionReader().load_session(context.state.session_id)
    if session is None or not session.transcript_path:
        raise PlanNotConfirmableError("대화 기록 경로가 없어 명령의 계획 id 를 읽지 못했습니다")
    return Path(session.transcript_path)


def _reviewing_plan(plan_id: int) -> Plan:
    """계획 저장소의 계획. 없거나 검토 중이 아니면 PlanNotConfirmableError."""
    try:
        plan = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as missing:
        raise PlanNotConfirmableError(f"계획 {plan_id} 이 계획 저장소에 없습니다") from missing
    if plan.status is not PlanStatus.REVIEWING:
        raise PlanNotConfirmableError(f"계획 {plan_id} 은 {status_label(plan.status.value)} 상태라 확정할 수 없습니다")
    return plan


def _shown_record(plan_id: int) -> ShownRecord:
    """이 작업 폴더에 남은, 계획을 보여 준 기록. 없으면 PlanNotConfirmableError."""
    shown = DefaultPlanFolderReader().read_shown(plan_id)
    if shown is None:
        raise PlanNotConfirmableError(
            f"계획 {plan_id} 을 이 작업 폴더에서 보여 준 기록이 없습니다. 계획을 만든 폴더에서 불러 주세요"
        )
    return shown
