"""show_plans: collect_plans 의 목록을 보이고, 명령 뒤에 계획 id 를 넣어 다시 부르라고 안내한다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.show_request import ShowRequest
from task_planner.workflow.list_plans.show_plans.plan_status_label import status_label

# 계획서(specs/plans/workflow-list_plans.md) show_plans 의 보일 글 그대로
GUIDE = "명령 뒤에 계획 id 를 넣어 다시 불러 주세요. 예: /task-planner:plan-go 7"
NO_PLANS = "이 작업 폴더에 계획이 없습니다. /task-planner:run make_plan 으로 계획을 만들어 주세요."


@TASKS.register_as("list_plans.show_plans")
class ShowPlansTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 계획이 있으면 다시 부르는 방법과 목록 표, 없으면 계획을 만드는 방법을 보인다
        return ShowRequest(build_plan_list_text(context.read("collect_plans")["plans"]))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def build_plan_list_text(plans: list[dict[str, Any]]) -> str:
    if not plans:
        return NO_PLANS
    rows = ["| id | 제목 | 상태 |", "|---|---|---|"]
    rows += [f"| {plan['plan_id']} | {plan['title']} | {status_label(plan['status'])} |" for plan in plans]
    return GUIDE + "\n\n" + "\n".join(rows)
