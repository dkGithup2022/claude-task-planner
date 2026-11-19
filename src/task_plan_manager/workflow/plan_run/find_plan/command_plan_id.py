"""대화에서 사용자가 마지막으로 친 /plan-run 명령의 계획 id 를 읽는다.
run 스킬 방식으로는 흐름에 인자를 넘길 수 없어, 대화 기록에 남은 명령 줄에서 읽는다 (confirm_plan 과 같은 방식)."""

from __future__ import annotations

import re
from pathlib import Path

from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError

# 대화 읽기 함수는 슬래시 명령을 "/task_plan_manager:plan-run 7" 처럼 "명령 인자" 한 줄로 넣어 준다
COMMAND_LINE = re.compile(r"^/\S*plan-run\s+(\d+)")


def command_plan_id(transcript: Path) -> int:
    """대화에서 사용자가 마지막으로 친 /plan-run 줄의 계획 id. 없으면 PlanNotRunnableError."""
    user_lines = [utterance.text.strip() for utterance in dialogue(transcript) if utterance.role == "user"]
    for line in reversed(user_lines):
        matched = COMMAND_LINE.match(line)
        if matched:
            return int(matched.group(1))
    raise PlanNotRunnableError(
        "명령에서 계획 id 를 찾지 못했습니다. /task_plan_manager:plan-run <계획 id> 로 다시 불러 주세요"
    )
