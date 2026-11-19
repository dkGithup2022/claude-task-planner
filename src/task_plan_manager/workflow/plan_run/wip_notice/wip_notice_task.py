"""wip_notice: 묶음 1 시험용 임시 끝 단계. 묶음 5 의 notify 로 바꾼다 (계획서 workflow-plan_run.md)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.workflow.plan_run.stopped_node import stopped_nodes


@TASKS.register_as("plan_run.wip_notice")
class WipNoticeTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        found = context.read("find_plan")
        stopped = stopped_nodes(context)
        if stopped:
            node_ids = ", ".join(str(node_id) for node_id in stopped)
            return ShowRequest(
                f"노드 {node_ids} 에서 멈췄습니다. 이어 하려면 /task_plan_manager:plan-run {found['plan_id']}"
            )
        return ShowRequest(
            f'계획 {found["plan_id"]} "{found["title"]}" 을 실행 중으로 두었습니다. '
            "(작업 지시 만들기부터는 아직 만들지 않았습니다)"
        )

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})
