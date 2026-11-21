"""write_request: interview 구간의 대화를 읽어, 사용자가 확인한 정리를 제목과 명령서 md 로 옮긴다 (claude -p, opus)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.claude_utils.transcript.read_dialogue import dialogue
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.workflow.make_plan.write_request.prompt_write_request_output import WriteRequestOutput
from task_planner.workflow.make_plan.write_request.transcript_missing_error import TranscriptMissingError

WRITE_REQUEST = PromptSpec(
    name="write_request",
    prompt_file=Path(__file__).parent / "prompt_write_request.md",
    output_type=WriteRequestOutput,
    model="opus",  # 사용자, 2026-11-19
)


@TASKS.register_as("make_plan.write_request")
class WriteRequestTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        # interview 구간의 대화를 "역할: 말" 줄로 이어 claude -p 의 입력 글로 넘긴다
        return PromptRequest(WRITE_REQUEST, build_write_request_input(context.read("interview")))

    def build_output(self, context: FlowContext, result: WriteRequestOutput) -> TaskOutput:
        # 제목과 명령서를 앞뒤 공백만 정리해 결과로 남긴다
        return TaskOutput({"title": result.title.strip(), "request": result.request.strip()})


def build_write_request_input(interview: dict[str, Any]) -> str:
    """대화 기록에서 interview 구간(from~to)의 사람·Claude 말만 뽑아 줄로 잇는다. 대화 기록 경로가 없으면 실패."""
    transcript = interview.get("transcript")
    if not transcript:
        raise TranscriptMissingError("interview 결과에 대화 기록 경로가 없습니다. 세션 시작 훅이 돌지 않았습니다")
    started_at, ended_at = interview["from"], interview["to"]
    utterances = [
        utterance for utterance in dialogue(Path(transcript), until=ended_at) if utterance.at[:19] >= started_at[:19]
    ]
    return "\n".join(f"{utterance.role}: {utterance.text}" for utterance in utterances)
