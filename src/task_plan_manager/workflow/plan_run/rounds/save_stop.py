"""이번 실행에서 사용자가 멈추기로 한 자리를 계획 폴더에 남긴다. 다음 차례의 run_nodes 가 읽고 바로 돌아온다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.local.plan_folder.dto.stop_mark import StopMark

FAILED_STOP = "failed_stop"
PROMPT_EDIT = "prompt_edit"
CONFIRM_DENIED = "confirm_denied"


def save_stop(context: FlowContext, plan_id: int, reason: str, node_id: int, message: str) -> None:
    DefaultPlanFolderWriter().save_stop(plan_id, StopMark(context.state.run_id, reason, (node_id,), message))


def again_line(plan_id: int) -> str:
    return f"이어 하려면 /task_plan_manager:plan-run {plan_id}"
