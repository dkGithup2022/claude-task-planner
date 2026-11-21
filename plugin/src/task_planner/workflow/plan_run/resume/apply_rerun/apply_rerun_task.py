"""apply_rerun (D 1-1): 모두 다시 실행이면 끊긴 노드를 전부 할 일(todo)로 되돌린다. 멈추기면 아무것도 쓰지 않는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.plan_api_choice import plan_api_writer
from task_planner.workflow.plan_run.resume.rerun_choices import STOP


@TASKS.register_as("plan_run.apply_rerun")
class ApplyRerunTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 모두 다시 실행이면 끊긴 노드마다 할 일로 되돌리고, 멈추기면 아무것도 쓰지 않는다
        if context.read("ask_rerun")["answer"] == STOP:
            return TaskOutput({"stopped": True})
        plan_id = context.read("find_plan")["plan_id"]
        for node in context.read("check_broken")["nodes"]:
            _back_to_todo(plan_id, int(node["node_id"]))
        return TaskOutput({"stopped": False})


def _back_to_todo(plan_id: int, node_id: int) -> None:
    """run.json 이 있으면 todo 로 되돌리고(회차 그대로), 계획 저장소의 노드 상태도 todo 로."""
    run = DefaultPlanFolderReader().read_run(plan_id, node_id)
    if run is not None:
        DefaultPlanFolderWriter().save_run(plan_id, node_id, run.back_to_todo())
    plan_api_writer().update_node(plan_id, node_id, NodeChange(status=PlanNodeStatus.TODO))
