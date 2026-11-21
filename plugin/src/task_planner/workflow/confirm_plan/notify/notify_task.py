"""notify: 확정 결과를 알린다 (사용자, 2026-11-18).
결정, 저장한 지식 수, 승인이면 /plan-run <id> 안내, 불허면 이 계획은 끝났다고 알린다.
결정 값은 선언의 Ref args 로 받는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.show_request import ShowRequest
from task_planner.workflow.confirm_plan.notify.saved_knowledge_count import saved_knowledge_count


@TASKS.register_as("confirm_plan.notify")
class NotifyTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def __init__(self, decision: str) -> None:
        self.decision = decision  # approved | rejected (선언의 Ref args)

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 결정, 저장한 지식 수, 다음에 할 일을 보인다
        found = context.read("find_plan")
        new_count, append_count = saved_knowledge_count(context)
        return ShowRequest(build_notice(self.decision, found["plan_id"], found["title"], new_count, append_count))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def build_notice(decision: str, plan_id: int, title: str, new_count: int, append_count: int) -> str:
    saved = f"저장한 지식 {new_count + append_count}개 (새로 {new_count}, 덧붙이기 {append_count})."
    if decision == "approved":
        return f'계획 {plan_id} "{title}" 을 승인했습니다. {saved}\n실행은 /task-planner:plan-run {plan_id}'
    return f'계획 {plan_id} "{title}" 을 불허했습니다. 이 계획은 끝났습니다. {saved}'
