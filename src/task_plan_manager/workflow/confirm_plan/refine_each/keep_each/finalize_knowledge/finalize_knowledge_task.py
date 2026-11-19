"""finalize_knowledge (C 3 단계, claude -p opus).
review_knowledge 대화에서 사용자가 마지막으로 확인한 본문과 저장 여부를 뽑는다."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_plan_manager.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.prompt_request import PromptRequest
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.finalize_knowledge.prompt_finalize_knowledge_output import (  # noqa: E501
    FinalizeKnowledgeOutput,
)

FINALIZE_KNOWLEDGE = PromptSpec(
    name="finalize_knowledge",
    prompt_file=Path(__file__).parent / "prompt_finalize_knowledge.md",
    output_type=FinalizeKnowledgeOutput,
    model="opus",
)


@TASKS.register_as("confirm_plan.finalize_knowledge")
class FinalizeKnowledgeTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        # 초안과, 초안을 다듬은 대화 구간을 입력 글로 넘긴다
        draft = context.read("write_knowledge")
        return PromptRequest(FINALIZE_KNOWLEDGE, build_finalize_input(draft, context.read("review_knowledge")))

    def build_output(self, context: FlowContext, result: FinalizeKnowledgeOutput) -> TaskOutput:
        return TaskOutput({"save": result.save, "theme": result.theme.strip(), "body": result.body.strip()})


def build_finalize_input(draft: dict[str, Any], review: dict[str, Any]) -> str:
    """'# 초안' (작업 이름, 본문) 과 '# 대화' (review_knowledge 구간의 사람·Claude 말)."""
    lines: list[str] = []
    if review.get("transcript"):
        lines = [
            f"{utterance.role}: {utterance.text}"
            for utterance in dialogue(Path(review["transcript"]), until=review["to"])
            if utterance.at[:19] >= review["from"][:19]
        ]
    talk = "\n".join(lines) or "(대화 없음. 초안 그대로 저장하기로 한 것으로 본다)"
    return f"# 초안\n작업 이름: {draft['theme']}\n본문:\n{draft['body']}\n\n# 대화\n{talk}"
