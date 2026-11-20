"""고른 병합 대상을 읽는다. 본문 쓰기, 확인 대화, 저장 단계가 같이 쓴다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_missing_error import OutputMissingError

TARGET_PAGES = ("choose_target_1", "choose_target_2", "choose_target_3")  # 병합 대상을 읽는 단계의 reads 에 넣는다


def merge_target_id(context: FlowContext) -> int | None:
    """고른 병합 대상의 id. 병합이 아니거나 새로 저장을 골랐으면 None."""
    for node_name in TARGET_PAGES:
        try:
            memory_id = context.read(node_name)["memory_id"]
        except OutputMissingError:  # 건너뛴 쪽
            continue
        if memory_id is not None:
            return int(memory_id)
    return None
