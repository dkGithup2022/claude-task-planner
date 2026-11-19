"""check_broken (D 1-1): 이어 갈 때, 실행 중으로 남은 계획 노드를 정리한다.
결과 파일이 있으면 끝까지 한 것이라 완료로 기록하고, 없으면 다시 실행할지 물을 목록에 넣는다
(기존 plan-run SKILL.md:19, 도식화 D 1-1)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.common.clock import utc_now
from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer


@TASKS.register_as("plan_run.check_broken")
class CheckBrokenTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 읽기: 계획의 노드 상태와 계획 폴더
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        folder = DefaultPlanFolderReader()
        running = [node for node in plan.nodes if node.status is PlanNodeStatus.RUNNING]
        # 판정: 결과 파일이 있으면 끝까지 한 것, 없으면 사용자에게 물을 것
        finished = [node for node in running if folder.read_output(plan_id, node.node_id) is not None]
        broken = [node for node in running if node not in finished]
        # 쓰기: 끝까지 한 노드를 완료로 기록한다
        for node in finished:
            _record_done(plan_id, node.node_id, folder.read_run(plan_id, node.node_id))
        return TaskOutput(
            {
                "nodes": [{"node_id": node.node_id, "title": node.title} for node in broken],
                "recorded_done": [node.node_id for node in finished],
            }
        )


def _record_done(plan_id: int, node_id: int, run: NodeRun | None) -> None:
    """노드 상태 done, run.json 에 끝난 시각. run.json 이 없으면(시작 기록 전에 끊김) 1회차로 만든다."""
    started = run or NodeRun(round=1, status=PlanNodeStatus.RUNNING)
    DefaultPlanFolderWriter().save_run(plan_id, node_id, started.finish(PlanNodeStatus.DONE, utc_now()))
    plan_api_writer().update_node(plan_id, node_id, NodeChange(status=PlanNodeStatus.DONE))
