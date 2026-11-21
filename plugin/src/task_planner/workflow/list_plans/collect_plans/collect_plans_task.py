"""collect_plans: 이 작업 폴더의 계획 id(.plan/ 폴더 이름)마다 계획 저장소에서 제목과 상태를 읽는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError

MISSING_TITLE = "(계획 저장소에 없음)"


@TASKS.register_as("list_plans.collect_plans")
class CollectPlansTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 작업 폴더의 계획 id 마다 계획 저장소에서 제목과 상태를 읽는다 (id 작은 순)
        plan_ids = DefaultPlanFolderReader().list_plan_ids()
        return TaskOutput({"plans": [_plan_row(plan_id) for plan_id in plan_ids]})


def _plan_row(plan_id: int) -> dict[str, Any]:
    """계획 하나의 id, 제목, 상태. 계획 저장소에 없으면 제목만 '(계획 저장소에 없음)', 상태는 빈 글."""
    try:
        plan = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError:
        return {"plan_id": plan_id, "title": MISSING_TITLE, "status": ""}
    return {"plan_id": plan_id, "title": plan.title, "status": plan.status.value}
