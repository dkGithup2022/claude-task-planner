"""계획을 보여 준 뒤의 피드백 대화를 대화 기록에서 잘라 낸다.
시작: 보여 준 시각.
끝: 그 구간에 /plan-go·/plan-cancel 줄이 있으면 마지막 그 줄 직전, 없으면(다른 대화에서 부른 경우) 파일 끝."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.claude_utils.transcript.dto.utterance import Utterance
from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.workflow.confirm_plan.find_plan.command_plan_id import COMMAND_LINE


def feedback_dialogue(transcript: Path, shown_at: str) -> list[Utterance]:
    """보여 준 시각부터 마지막 확정 명령 줄 직전까지의 사람·Claude 말."""
    after_shown = [utterance for utterance in dialogue(transcript) if utterance.at[:19] >= shown_at[:19]]
    command_indexes = [
        index
        for index, utterance in enumerate(after_shown)
        if utterance.role == "user" and COMMAND_LINE.match(utterance.text.strip())
    ]
    return after_shown[: command_indexes[-1]] if command_indexes else after_shown
