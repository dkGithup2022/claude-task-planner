"""choose_action (C 1·2 단계를 한 질문으로, 사용자 2026-11-19).
후보마다 새로 저장 / 기존 지식에 덧붙이기 / 넣지 않기를 묻는다.
선택지를 눌렀을 때 기존 지식을 옆에 보이는 기능이 없어,
질문 글에 기존 지식 두 개를 KNOWLEDGE SEARCHED 모양으로 넣는다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.workflow.confirm_plan.refine_each.candidate_kind import type_label
from task_plan_manager.workflow.confirm_plan.refine_each.choose_action.action_choices import (
    MAX_APPEND_TARGETS,
    action_choices,
)

BODY_PREVIEW_CHARS = 200  # 질문 글에 보일 기존 지식 본문 길이


@TASKS.register_as("confirm_plan.choose_action")
class ChooseActionTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        # 후보와 기존 지식 두 개를 보이고, 새로 저장 / 덧붙이기 / 넣지 않기 가운데 하나를 고르게 한다
        existing = context.read("find_existing")["existing"]
        total = len(context.read("extract_knowledge")["candidates"])
        question = build_question(context.current_item(), existing, context.item_key or "1", total)
        return QuestionRequest(question, action_choices(existing))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 선택지 밖의 답이면 같은 질문을 다시 낸다
        if result not in action_choices(context.read("find_existing")["existing"]):
            raise ReplyRejectedError(f"선택지 밖의 답: {result}")
        return TaskOutput({"answer": result})


def build_question(candidate: dict[str, Any], existing: list[dict[str, Any]], number: str, total: int) -> str:
    quotes = ", ".join(f'"{quote}"' for quote in candidate["quotes"])
    lines = [
        f"지식 후보 {number}/{total}: {type_label(candidate['type'])} {candidate['theme']}",
        candidate["content"],
        f"근거: {quotes}",
    ]
    for order, memory in enumerate(existing[:MAX_APPEND_TARGETS], start=1):
        body = memory["body"][:BODY_PREVIEW_CHARS] + ("…" if len(memory["body"]) > BODY_PREVIEW_CHARS else "")
        lines += ["", f"****** KNOWLEDGE SEARCHED {order} ********", f"#{memory['memory_id']} {memory['theme']}", body]
    lines += ["", "이 후보를 어떻게 할까요?"]
    return "\n".join(lines)
