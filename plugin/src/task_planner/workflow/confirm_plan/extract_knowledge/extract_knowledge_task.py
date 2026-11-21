"""extract_knowledge: 계획을 보여 준 뒤의 피드백 대화에서 다음 계획에도 쓸 지식 후보를 뽑는다 (claude -p, opus).
후보의 종류는 plan(일을 나누는 방식)과 domain(그 일을 하는 방법·규칙) 두 가지다 (사용자, 2026-11-19).
결과의 candidates 를 C(refine_each)가 후보마다 반복한다. 비면 C 는 0 번 돈다."""

from __future__ import annotations

from pathlib import Path

from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.model.plan.plan import Plan
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.workflow.confirm_plan.extract_knowledge.feedback_dialogue import feedback_dialogue
from task_planner.workflow.confirm_plan.extract_knowledge.knowledge_candidate import KnowledgeCandidate
from task_planner.workflow.confirm_plan.extract_knowledge.prompt_extract_knowledge_output import (
    ExtractKnowledgeOutput,
)
from task_planner.workflow.confirm_plan.find_plan.plan_not_confirmable_error import PlanNotConfirmableError
from task_planner.workflow.confirm_plan.show_progress import show_knowledge_step

MAX_CANDIDATES = 16  # 후보가 많으면 앞의 16 개만 다룬다 (사용자, 2026-11-18)
CANDIDATE_TYPES = ("plan", "domain")

EXTRACT_KNOWLEDGE = PromptSpec(
    name="extract_knowledge",
    prompt_file=Path(__file__).parent / "prompt_extract_knowledge.md",
    output_type=ExtractKnowledgeOutput,
    model="opus",
)


@TASKS.register_as("confirm_plan.extract_knowledge")
class ExtractKnowledgeTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        show_knowledge_step(context, ReinforcePhase.EXTRACT)
        # 계획의 노드 목록과, 계획을 보여 준 뒤의 피드백 대화를 입력 글로 넘긴다
        found = context.read("find_plan")
        plan = plan_api_reader().get_plan(found["plan_id"])
        return PromptRequest(EXTRACT_KNOWLEDGE, build_extract_input(plan, found["transcript"], found["shown_at"]))

    def build_output(self, context: FlowContext, result: ExtractKnowledgeOutput) -> TaskOutput:
        # 쓸 수 없는 후보를 버리고 앞의 16 개만 남긴다
        warnings: list[str] = []
        kept = [candidate for candidate in result.candidates if _is_usable(candidate, warnings)]
        if len(kept) > MAX_CANDIDATES:
            warnings.append(f"후보 {len(kept)} 개 가운데 앞의 {MAX_CANDIDATES} 개만 다룹니다")
        return TaskOutput(
            {"candidates": [_to_data(candidate) for candidate in kept[:MAX_CANDIDATES]], "warnings": warnings}
        )


def build_extract_input(plan: Plan, transcript: str | None, shown_at: str) -> str:
    """'# 계획' (제목, 노드 id 와 제목) 과 '# 대화' (보여 준 뒤의 '역할: 말' 줄)."""
    if not transcript:
        raise PlanNotConfirmableError("계획을 보여 준 대화의 기록 경로가 없어 지식을 뽑지 못했습니다")
    node_lines = "\n".join(f"- {node.node_id} {node.title}" for node in plan.nodes)
    talk_lines = "\n".join(
        f"{utterance.role}: {utterance.text}" for utterance in feedback_dialogue(Path(transcript), shown_at)
    )
    return f"# 계획\n제목: {plan.title}\n{node_lines}\n\n# 대화\n{talk_lines or '(대화 없음)'}"


def _is_usable(candidate: KnowledgeCandidate, warnings: list[str]) -> bool:
    if candidate.type not in CANDIDATE_TYPES:
        warnings.append(f'종류가 "{candidate.type}" 인 후보를 버림: {candidate.theme}')
        return False
    if not candidate.theme.strip() or not candidate.content.strip():
        warnings.append(f"작업 이름이나 내용이 빈 후보를 버림: {candidate.theme or candidate.content}")
        return False
    return True


def _to_data(candidate: KnowledgeCandidate) -> dict[str, object]:
    return {
        "type": candidate.type,
        "theme": candidate.theme.strip(),
        "content": candidate.content.strip(),
        "quotes": list(candidate.quotes),
    }
