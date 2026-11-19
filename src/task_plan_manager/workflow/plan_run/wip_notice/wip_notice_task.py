"""wip_notice: 시험용 임시 끝 단계. 묶음 5 의 notify 로 바꾼다 (계획서 workflow-plan_run.md)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.output_missing_error import OutputMissingError
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.workflow.plan_run.stopped_node import BROKEN, stop_point


@TASKS.register_as("plan_run.wip_notice")
class WipNoticeTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        found = context.read("find_plan")
        again = f"이어 하려면 /task_plan_manager:plan-run {found['plan_id']}"
        stopped = stop_point(context)
        if stopped is not None:
            node_ids = ", ".join(str(node_id) for node_id in stopped.node_ids)
            if stopped.reason == BROKEN:
                return ShowRequest(f"노드 {node_ids} 에서 멈췄습니다. {again}")
            return ShowRequest(f"노드 {node_ids} 의 작업 지시를 만들지 못해 멈췄습니다. {again}")
        return ShowRequest(
            f'계획 {found["plan_id"]} "{found["title"]}" 을 실행 중으로 두었습니다. '
            f"작업 지시 {_made_count(context)}개를 새로 만들었습니다. (노드 실행부터는 아직 만들지 않았습니다)"
        )

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def _made_count(context: FlowContext) -> int:
    """write_prompts 와 retry_prompts 가 만든 작업 지시 수. 건너뛴 단계는 0."""
    count = 0
    for node_name in ("write_prompts", "retry_prompts"):
        try:
            count += len(context.read(node_name)["made"])
        except OutputMissingError:
            continue
    return count
