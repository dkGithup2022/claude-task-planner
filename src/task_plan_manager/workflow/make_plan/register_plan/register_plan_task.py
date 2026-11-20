"""register_plan: write_request 의 제목과 명령서로 계획을 등록하고, 받은 plan_id 로 이 작업 폴더에 계획 폴더를 만든다.
참여 페르소나는 첫 판에서 페르소나 목록의 첫 페르소나 하나다 (사용자, 2026-11-19). 고르기는 나중에 더한다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.persona_api.persona_api_choice import persona_api_reader
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_writer
from task_plan_manager.workflow.make_plan.register_plan.no_persona_error import NoPersonaError
from task_plan_manager.workflow.make_plan.show_progress import show_planning_started


@TASKS.register_as("make_plan.register_plan")
class RegisterPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 명령서로 계획을 등록하고, 받은 id 로 이 작업 폴더에 계획 폴더를 만든 뒤 상태 줄에 진행을 보이기 시작한다
        written = context.read("write_request")
        new_plan = NewPlan(title=written["title"], request=written["request"], persona_ids=_default_persona_ids())
        plan = plan_api_writer().create_plan(new_plan)
        DefaultPlanFolderWriter().create_plan(plan.plan_id, written["request"])
        show_planning_started(plan.plan_id)
        return TaskOutput({"plan_id": plan.plan_id})


def _default_persona_ids() -> tuple[int, ...]:
    """첫 판의 참여 페르소나: 페르소나 목록의 첫 페르소나 하나. 없으면 NoPersonaError."""
    personas = persona_api_reader().list_personas()
    if not personas:
        raise NoPersonaError("페르소나 목록이 비어 있어 계획을 등록하지 못했습니다")
    return (personas[0].persona_id,)
