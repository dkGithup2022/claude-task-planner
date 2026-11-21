"""choose_action (C 1·2 단계를 한 질문으로, 사용자 2026-11-19).
후보마다 질문 글에 비슷한 지식(10 개까지)을 한 줄씩 보이고, 병합 / 새로 저장 / 넣지 않기를 묻는다.
병합할 지식은 다음 단계(choose_target)에서 고른다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.workflow.confirm_plan.refine_each.candidate_kind import type_label
from task_planner.workflow.confirm_plan.refine_each.choose_action.action_choices import action_choices
from task_planner.workflow.confirm_plan.show_progress import show_knowledge_step

BODY_PREVIEW_CHARS = 80  # 질문 글의 목록 한 줄에 보일 기존 지식 본문 길이


@TASKS.register_as("confirm_plan.choose_action")
class ChooseActionTask(Task):
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> QuestionRequest:
        show_knowledge_step(context, ReinforcePhase.CHOOSE)
        # 후보와 비슷한 지식 목록을 보이고, 병합 / 새로 저장 / 넣지 않기 가운데 하나를 고르게 한다
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
        "",
    ]
    if existing:
        lines.append(f"비슷한 지식 {len(existing)}개")
        lines += [f"{order:>2}. {_one_line(memory)}" for order, memory in enumerate(existing, start=1)]
        lines += ["", "병합하시겠습니까?"]
    else:
        lines += ["비슷한 지식이 없습니다.", "", "이 후보를 어떻게 할까요?"]
    return "\n".join(lines)


def _one_line(memory: dict[str, Any]) -> str:
    """목록 한 줄: id, 작업 이름, 본문 앞부분 (줄바꿈은 공백으로)."""
    body = " ".join(memory["body"].split())
    short = body[:BODY_PREVIEW_CHARS] + ("…" if len(body) > BODY_PREVIEW_CHARS else "")
    return f"#{memory['memory_id']} {memory['theme']} — {short}"
