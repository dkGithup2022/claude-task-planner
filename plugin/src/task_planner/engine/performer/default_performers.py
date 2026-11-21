"""default_performers: 수행자 6개를 PerformedBy 별로 묶는다 (메인 세션 판단은 아직 없음)."""

from __future__ import annotations

from task_planner.engine.performer.claude_prompt.claude_prompt_performer import ClaudePromptPerformer
from task_planner.engine.performer.code.code_performer import CodePerformer
from task_planner.engine.performer.main_session.main_session_ask_performer import MainSessionAskPerformer
from task_planner.engine.performer.main_session.main_session_show_performer import MainSessionShowPerformer
from task_planner.engine.performer.main_session.main_session_talk_performer import MainSessionTalkPerformer
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.performer.subagent.subagent_performer import SubagentPerformer
from task_planner.engine.performer.task_performer import TaskPerformer
from task_planner.engine.port.session.session_reader import SessionReader


def default_performers(session_reader: SessionReader) -> dict[PerformedBy, TaskPerformer]:
    items: list[TaskPerformer] = [
        CodePerformer(), ClaudePromptPerformer(), MainSessionShowPerformer(), MainSessionAskPerformer(),
        MainSessionTalkPerformer(session_reader), SubagentPerformer(),
    ]  # fmt: skip
    return {p.performed_by: p for p in items}
