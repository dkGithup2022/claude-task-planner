"""notify (D 6): 끝 알림. 멈췄으면 멈춘 자리, 끝났거나 막혔으면 노드별 표, 그 밖이면 남은 노드 안내.
흐름의 마지막 보이기 단계라 이 글은 끝 지시(finished)에 실려 사용자에게 보인다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_schedule import plan_progress
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.plan_run.notify.notify_messages import (
    blocked_message,
    finished_message,
    remaining_message,
    stopped_message,
)
from task_plan_manager.workflow.plan_run.stopped_node import stop_point


@TASKS.register_as("plan_run.notify")
class NotifyTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        plan_id = context.read("find_plan")["plan_id"]

        stopped = stop_point(context)
        if stopped is not None:
            return ShowRequest(stopped_message(stopped, plan_id))

        plan = plan_api_reader().get_plan(plan_id)
        node_runs = read_node_runs(plan)

        if plan_is_finished(context):
            return ShowRequest(finished_message(plan, node_runs))
        if plan_progress(plan).blocked:
            return ShowRequest(blocked_message(plan, node_runs))
        return ShowRequest(remaining_message(plan))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def plan_is_finished(context: FlowContext) -> bool:
    """앞 단계 finish_plan 이 모든 노드가 완료·건너뜀이라고 판정했는지."""
    return bool(context.read("finish_plan")["finished"])


def read_node_runs(plan: Plan) -> dict[int, NodeRun | None]:
    """노드마다 run.json 기록. 실행한 적 없는 노드는 None."""
    folder = DefaultPlanFolderReader()
    return {node.node_id: folder.read_run(plan.plan_id, node.node_id) for node in plan.nodes}
