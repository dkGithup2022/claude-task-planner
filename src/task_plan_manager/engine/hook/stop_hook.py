"""Stop 훅: 멈추려 할 때 할 일이 남았으면 막는다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.instruction.instruction_type import InstructionType
from task_plan_manager.engine.model.run_state.flow_run_status import FlowRunStatus
from task_plan_manager.engine.port.run_state.run_state_reader import RunStateReader
from task_plan_manager.engine.port.session.session_reader import SessionReader


def on_stop(sid: str, data: dict[str, Any], sessions: SessionReader, runs: RunStateReader) -> dict[str, Any] | None:
    """막는 때: 이 세션이 연 실행이 진행 중이고, 기다리는 지시가 없거나(next 차례) spawn 일 때.
    다른 명령이 단계를 실행 중이면 막지 않는다 (백그라운드로 넘어간 명령의 완료 알림을 기다린다)."""
    if data.get("stop_hook_active"):
        return None
    session = sessions.load_session(sid)
    if session is None or session.active_run_id is None:
        return None
    state = runs.load_run(sid, session.active_run_id)
    if state.status is not FlowRunStatus.RUNNING:
        return None
    if state.executing is not None and state.executing.is_alive():
        return None
    waiting = state.waiting_instruction
    if waiting is None:
        reason = "task_plan_manager 실행이 진행 중입니다. " + "task_plan_manager next 로 다음 지시를 받으세요."
        return {"decision": "block", "reason": reason}
    if waiting.type is InstructionType.SPAWN:
        reason = "서브에이전트를 띄우고, 완료 알림이 온 뒤 task_plan_manager done 을 부르세요."
        return {"decision": "block", "reason": reason}
    return None
