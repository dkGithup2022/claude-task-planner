"""choose_target: 병합할 지식을 쪽 하나에서 고른다. 다음 쪽이 있으면 넷째 선택지가 "다음 3개 보기"다.
쪽마다 단계를 하나씩 두고, 같은 클래스에 쪽 번호만 넘긴다 (사용자, 2026-11-19: 다음 3개 보기로 넘겨 보기).
engine 은 한 흐름에서 같은 등록 키를 두 번 쓰지 못하게 하므로, 쪽마다 키를 따로 등록한다."""

from __future__ import annotations

import re
from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.workflow.confirm_plan.refine_each.choose_action.action_choices import NEW
from task_plan_manager.workflow.confirm_plan.refine_each.choose_target.target_pages import (
    NEXT_PAGE,
    has_next,
    page_of,
    page_range,
)

_MEMORY_ID = re.compile(r"^#(\d+) ")


@TASKS.register_as("confirm_plan.choose_target_3")
@TASKS.register_as("confirm_plan.choose_target_2")
@TASKS.register_as("confirm_plan.choose_target_1")
class ChooseTargetTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def __init__(self, page: int) -> None:
        self.page = page

    def build_request(self, context: FlowContext) -> QuestionRequest:
        # 이 쪽의 지식을 선택지로 보이고, 뒤에 쪽이 더 있으면 "다음 3개 보기"를 붙인다
        existing = context.read("find_existing")["existing"]
        question = f"어느 지식에 병합할까요? ({page_range(existing, self.page)})"
        return QuestionRequest(question, target_choices(existing, self.page))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 선택지 밖의 답이면 같은 질문을 다시 낸다
        if result not in target_choices(context.read("find_existing")["existing"], self.page):
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        matched = _MEMORY_ID.match(result)
        return TaskOutput({"answer": result, "memory_id": int(matched.group(1)) if matched else None})


def target_choices(existing: list[dict[str, Any]], page: int) -> tuple[str, ...]:
    """이 쪽의 선택지. 지식이 하나뿐이면 선택 창을 띄울 수 있게 "새 지식으로 저장"을 더한다."""
    labels = tuple(f"#{memory['memory_id']} {memory['theme']}" for memory in page_of(existing, page))
    if has_next(existing, page):
        return (*labels, NEXT_PAGE)
    return labels if len(labels) > 1 else (*labels, NEW)
