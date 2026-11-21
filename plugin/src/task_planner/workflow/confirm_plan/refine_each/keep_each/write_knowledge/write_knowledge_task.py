"""write_knowledge (C 3 단계 본문 초안, claude -p opus): 후보 하나의 본문(설명과 예시 3~4개)을 쓴다.
예시의 조건은 사용자가 정했다 (2026-11-19): 간단하면서 지식의 사례를 잘 나타내고, 여러 기법이 섞이지 않게."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.workflow.confirm_plan.refine_each.candidate_kind import memory_kind
from task_planner.workflow.confirm_plan.refine_each.choose_target.merge_target import merge_target_id
from task_planner.workflow.confirm_plan.refine_each.keep_each.write_knowledge.prompt_write_knowledge_output import (  # noqa: E501
    WriteKnowledgeOutput,
)
from task_planner.workflow.confirm_plan.refine_each.keep_each.write_knowledge.quoted_context import (
    quoted_context,
)
from task_planner.workflow.confirm_plan.show_progress import show_knowledge_step

WRITE_KNOWLEDGE = PromptSpec(
    name="write_knowledge",
    prompt_file=Path(__file__).parent / "prompt_write_knowledge.md",
    output_type=WriteKnowledgeOutput,
    model="opus",
)


@TASKS.register_as("confirm_plan.write_knowledge")
class WriteKnowledgeTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        show_knowledge_step(context, ReinforcePhase.DRAFT)
        # 후보, 그 근거가 나온 대화, 덧붙이기면 그 기존 지식을 입력 글로 넘긴다
        candidate = context.current_item()
        found = context.read("find_plan")
        target_id = merge_target_id(context)
        target = next((m for m in context.read("find_existing")["existing"] if m["memory_id"] == target_id), None)
        conversation = quoted_context(Path(found["transcript"]), found["shown_at"], candidate["quotes"])
        return PromptRequest(WRITE_KNOWLEDGE, build_write_input(candidate, conversation, target))

    def build_output(self, context: FlowContext, result: WriteKnowledgeOutput) -> TaskOutput:
        return TaskOutput({"theme": result.theme.strip(), "body": result.body.strip()})


def build_write_input(candidate: dict[str, Any], conversation: str, target: dict[str, Any] | None) -> str:
    parts = [
        "# 후보\n"
        f"종류: {candidate['type']} ({memory_kind(candidate['type']).value})\n"
        f"작업 이름: {candidate['theme']}\n"
        f"내용: {candidate['content']}",
        "# 사용자 말과 바로 앞의 Claude 말\n" + conversation,
    ]
    if target is not None:
        parts.append(f"# 덧붙일 기존 지식\n#{target['memory_id']} {target['theme']}\n{target['body']}")
    return "\n\n".join(parts)
