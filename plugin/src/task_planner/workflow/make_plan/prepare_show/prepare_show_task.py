"""prepare_show: 계획을 검토 중으로 바꾸고, 보여 준 기록을 계획 폴더에 남기고, 사용자에게 보일 글을 만든다.
보여 준 기록(시각, 대화 기록 경로)은 B 의 지식 추출이 계획 id 로 찾아 읽는다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_planner.common.clock import utc_now
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.model.plan.shown_record import ShownRecord
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_planner.workflow.make_plan.prepare_show.plan_not_showable_error import PlanNotShowableError
from task_planner.workflow.make_plan.prepare_show.plan_summary import build_summary


@TASKS.register_as("make_plan.prepare_show")
class PrepareShowTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획을 검토 중으로 바꾸고, 보여 준 기록을 남기고, 사용자에게 보일 글을 만든다
        plan_id = context.read("register_plan")["plan_id"]
        plan = _move_to_reviewing(plan_id)
        shown = ShownRecord(shown_at=utc_now(), transcript=context.read("interview")["transcript"])
        DefaultPlanFolderWriter().save_shown(plan_id, shown)
        return TaskOutput({"summary": build_summary(plan, context.read("split_plan")["warnings"])})


def _move_to_reviewing(plan_id: int) -> Plan:
    """작성 중이면 검토 중으로 바꾼다. 이미 검토 중이면 그대로. 그 밖이면 PlanNotShowableError."""
    plan = plan_api_reader().get_plan(plan_id)
    if plan.status is PlanStatus.REVIEWING:
        return plan
    if not plan.status.can_move_to(PlanStatus.REVIEWING):
        raise PlanNotShowableError(f"계획 {plan_id} 는 {plan.status.value} 상태라 검토 중으로 바꿀 수 없습니다")
    return plan_api_writer().set_plan_status(plan_id, PlanStatus.REVIEWING)
