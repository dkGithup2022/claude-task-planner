"""claude -p 를 부르는 함수의 모양. 실제로는 call_prompt, 시험에서는 가짜를 넘긴다."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec

PromptCaller = Callable[[PromptSpec, str], tuple[Any, PromptCallRecord]]
