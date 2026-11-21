"""continue_notice (D 3): 마감으로 "계속"이 된 차례에 마친 노드와 결과 위치를 보인다.
알림 단계라 next 가 여기서 끝나고 메인 세션으로 돌아간다 (plan_run_flow.py 주석 참고)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.show_request import ShowRequest
from task_planner.model.plan.plan_schedule import FINISHED
from task_planner.port.local.plan_folder.plan_folder_location import result_file
from task_planner.port.plan_api.plan_api_choice import plan_api_reader


@TASKS.register_as("plan_run.continue_notice")
class ContinueNoticeTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        ran_ids = [record["node_id"] for record in context.read("run_nodes")["ran"]]
        remaining = sum(1 for node in plan.nodes if node.status not in FINISHED)
        lines = [f"노드 {len(ran_ids)}개를 마쳤습니다. 남은 노드 {remaining}개를 이어서 실행합니다."]
        for node_id in ran_ids:
            path = result_file(plan_id, node_id).relative_to(Path.cwd())
            lines.append(f'- 노드 {node_id} "{plan.node(node_id).title}": {path}')
        return ShowRequest("\n".join(lines))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})
