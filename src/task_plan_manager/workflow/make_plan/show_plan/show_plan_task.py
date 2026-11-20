"""show_plan: prepare_show 가 만든 글을 사용자에게 보이고, 고치는 방법과 확정·불허 명령을 계획 id 까지 넣어 안내한다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.workflow.make_plan.show_progress import show_feedback_turn

# 계획서(specs/plans/workflow-make_plan.md) show_plan 의 보일 글 그대로
GUIDE = """고칠 곳이 있으면 대화로 말해 주세요.
확정은 /plan-go {plan_id}, 불허는 /plan-cancel {plan_id}"""
FEEDBACK_SKILL = "task_plan_manager:plan-feedback"


@TASKS.register_as("make_plan.show_plan")
class ShowPlanTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 보일 글 아래에 다음 명령을 계획 id 까지 넣어 붙인다 (사용자, 2026-11-19)
        summary = context.read("prepare_show")["summary"]
        plan_id = context.read("register_plan")["plan_id"]
        show_feedback_turn(plan_id)
        # 보인 뒤 메인 세션이 고치기 대화 스킬을 부른다. 마지막 단계라 이 글과 스킬이 끝 지시에 실린다
        return ShowRequest(f"{summary}\n\n{GUIDE.format(plan_id=plan_id)}", f"{FEEDBACK_SKILL} {plan_id}")

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})
