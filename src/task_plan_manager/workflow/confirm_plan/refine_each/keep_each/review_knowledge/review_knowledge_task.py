"""review_knowledge (C 3 단계 확인, 메인 세션 대화).
본문 초안을 보이고, 고칠 말이나 실제 사례를 받아 다듬으며 확인받는다.
고친 결과는 다음 단계(finalize_knowledge)가 이 대화에서 뽑는다 (사용자, 2026-11-19)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.conversation_request import ConversationRequest
from task_plan_manager.workflow.confirm_plan.refine_each.candidate_kind import type_label
from task_plan_manager.workflow.confirm_plan.refine_each.choose_target.merge_target import merge_target_id

GOAL = (Path(__file__).parent / "review_goal.md").read_text(encoding="utf-8").strip()
ASK_LINE = "이대로 저장할까요? 고칠 곳이나, 예시로 넣을 실제 사례가 있으면 말씀해 주세요."


@TASKS.register_as("confirm_plan.review_knowledge")
class ReviewKnowledgeTask(Task):
    request_type = ConversationRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ConversationRequest:
        # 초안을 보이는 글로 대화를 시작한다. 다듬는 대화는 run 스킬 글을 따르는 메인 세션이 한다
        draft = context.read("write_knowledge")
        target_id = merge_target_id(context)
        opening = build_opening(context.current_item(), draft, target_id)
        return ConversationRequest(goal=GOAL, opening=opening)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput(dict(result))


NOTHING_TO_ADD = (
    "기존 지식 #{target_id} 에 이미 같은 내용이 있어 덧붙일 것이 없습니다.\n\n"
    "저장하지 않을까요? 더할 사례나 규칙이 있으면 말씀해 주세요."
)


def build_opening(candidate: dict[str, Any], draft: dict[str, Any], target_id: int | None) -> str:
    where = f"#{target_id} 에 덧붙이기" if target_id is not None else "새 지식"
    if not draft["body"]:
        return f"{type_label(candidate['type'])} {draft['theme']} ({where})\n" + NOTHING_TO_ADD.format(
            target_id=target_id
        )
    label = "덧붙일 내용" if target_id is not None else "본문"
    return f"{type_label(candidate['type'])} {draft['theme']} ({where})\n{label}:\n{draft['body']}\n\n{ASK_LINE}"
