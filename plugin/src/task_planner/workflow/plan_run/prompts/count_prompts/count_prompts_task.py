"""count_prompts (D 2): 작업 지시가 아직 없는 노드와 대략의 시간·비용.
prompt.md 가 이미 있으면 사람이 고쳤든 아니든 만들지 않는다 (사용자, 2026-11-19).
시간·비용은 기존 안내(노드 하나에 1분 안팎, $0.3~0.6, plan-go/procedure.md:51)와 3개씩 동시로 계산한다."""

from __future__ import annotations

import math
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.workflow.plan_run.prompts.write_prompts.write_node_prompts import PARALLEL

COST_LOW_PER_NODE = 0.3
COST_HIGH_PER_NODE = 0.6


@TASKS.register_as("plan_run.count_prompts")
class CountPromptsTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 작업 지시가 아직 없는 노드만 고른다
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        folder = DefaultPlanFolderReader()
        missing = [node for node in plan.nodes if folder.read_prompt(plan_id, node.node_id) is None]
        return TaskOutput(
            {
                "missing": [{"node_id": node.node_id, "title": node.title} for node in missing],
                "minutes": math.ceil(len(missing) / PARALLEL),
                "cost_low": round(len(missing) * COST_LOW_PER_NODE, 1),
                "cost_high": round(len(missing) * COST_HIGH_PER_NODE, 1),
            }
        )
