"""지금 대화의 기록 파일. 세션 시작 훅이 session.json 에 남긴 경로."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.port.session.default_session_reader import DefaultSessionReader
from task_plan_manager.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError


def current_transcript(context: FlowContext) -> Path:
    """세션 시작 훅이 남긴 대화 기록 경로. 없으면 PlanNotRunnableError."""
    session = DefaultSessionReader().load_session(context.state.session_id)
    if session is None or not session.transcript_path:
        raise PlanNotRunnableError("대화 기록 경로가 없어 명령의 계획 id 를 읽지 못했습니다")
    return Path(session.transcript_path)
