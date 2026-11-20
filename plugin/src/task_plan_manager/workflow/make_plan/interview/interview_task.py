"""interview: 메인 세션이 grill-me 방식으로 사용자를 인터뷰해, 계획을 세우는 데 필요한 결정을 모은다.
결과는 대화 구간과 대화 기록 경로. 다음 단계(write_request)가 이 구간의 대화로 명령서를 쓴다."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.conversation_request import ConversationRequest

# 대화 목표는 계획서(specs/plans/workflow-make_plan.md) interview 의 글 그대로. 길어서 md 파일로 둔다
GOAL = (Path(__file__).parent / "interview_goal.md").read_text(encoding="utf-8").strip()

OPENING = "어떤 일을 계획으로 만들까요?"


@TASKS.register_as("make_plan.interview")
class InterviewTask(Task):
    request_type = ConversationRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ConversationRequest:
        # 메인 세션에 대화 목표와 첫 말을 넘긴다. 대화는 run 스킬 글을 따르는 메인 세션이 한다
        return ConversationRequest(goal=GOAL, opening=OPENING)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 수행자가 돌려준 대화 구간과 대화 기록 경로를 그대로 이 단계의 결과로 남긴다
        return TaskOutput(dict(result))
