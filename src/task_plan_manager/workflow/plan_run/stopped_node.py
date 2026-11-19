"""이번 실행에서 사용자가 멈추기를 고른 노드. 멈춘 뒤의 단계를 건너뛰는 조건과 알림이 같이 쓴다.
지금은 끊긴 노드 질문(ask_rerun)의 멈추기만 본다. 뒤 묶음(작업 지시, 노드 실행)의 멈춤은 그 묶음에서 더한다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_missing_error import OutputMissingError


def stopped_nodes(context: FlowContext) -> list[int]:
    """멈추기를 고른 자리의 노드 id.
    멈추지 않았거나, 끊긴 노드를 묻지 않았으면(이어 가기가 아님, 끊긴 노드 없음) 빈 목록."""
    try:
        stopped = context.read("apply_rerun")["stopped"]
    except OutputMissingError:
        return []
    if not stopped:
        return []
    return [int(node["node_id"]) for node in context.read("check_broken")["nodes"]]
