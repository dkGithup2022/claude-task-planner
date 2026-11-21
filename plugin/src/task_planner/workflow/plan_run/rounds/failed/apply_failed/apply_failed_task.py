"""apply_failed (D 5): 실패 처리 답대로 기록한다.
다시 실행: 지금 회차를 runs/<회차>/ 로 보관하고 회차 +1, 노드 todo. 다음 차례에 실행된다.
작업 지시를 고쳐 다시: 위와 같고 멈춘다. 사용자가 prompt.md 를 고친 뒤 /plan-run 을 다시 부른다.
건너뛰기: 그 노드와, 그 노드에만 기대는 뒤 노드를 건너뜀으로 (기존 run.py:263-293).
멈추기: 멈춘다. 계획은 실행 중으로 남는다."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from task_planner.common.clock import utc_now
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_schedule import nodes_to_skip
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.local.plan_folder.plan_folder_location import prompt_file
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_planner.workflow.plan_run.rounds.failed.failed_choices import EDIT_AND_RERUN, RERUN, SKIP
from task_planner.workflow.plan_run.rounds.save_stop import FAILED_STOP, PROMPT_EDIT, again_line, save_stop

SKIPPED_BY_USER = "사용자가 건너뜀"


@TASKS.register_as("plan_run.apply_failed")
class ApplyFailedTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        plan_id = context.read("find_plan")["plan_id"]
        node_id = int(context.read("run_nodes")["node_id"])
        answer = context.read("ask_failed")["answer"]
        title = plan_api_reader().get_plan(plan_id).node(node_id).title
        if answer in (RERUN, EDIT_AND_RERUN):
            _back_to_todo_with_next_round(plan_id, node_id)
        if answer == EDIT_AND_RERUN:
            path = prompt_file(plan_id, node_id).resolve()
            save_stop(
                context,
                plan_id,
                PROMPT_EDIT,
                node_id,
                f"작업 지시 {path} 를 고친 뒤 /task-planner:plan-run {plan_id}",
            )
        if answer == SKIP:
            return TaskOutput({"skipped": list(_skip_with_followers(plan_id, node_id))})
        if answer not in (RERUN, EDIT_AND_RERUN, SKIP):
            save_stop(
                context,
                plan_id,
                FAILED_STOP,
                node_id,
                f'노드 {node_id} "{title}" 에서 멈췄습니다. {again_line(plan_id)}',
            )
        return TaskOutput({"skipped": []})


def _back_to_todo_with_next_round(plan_id: int, node_id: int) -> None:
    """지금 회차의 결과를 보관하고 회차를 올린다 (run.json 은 todo 가 된다). 노드 상태도 todo."""
    DefaultPlanFolderWriter().archive_round(plan_id, node_id)
    plan_api_writer().update_node(plan_id, node_id, NodeChange(status=PlanNodeStatus.TODO))


def _skip_with_followers(plan_id: int, node_id: int) -> tuple[int, ...]:
    """그 노드와 그 노드에만 기대는 뒤 노드를 건너뜀으로. run.json 에 이유를 남긴다."""
    skipped = nodes_to_skip(plan_api_reader().get_plan(plan_id), node_id)
    folder, writer = DefaultPlanFolderReader(), DefaultPlanFolderWriter()
    for skipped_id in skipped:
        run = folder.read_run(plan_id, skipped_id) or NodeRun(round=1, status=PlanNodeStatus.TODO)
        finished = replace(run.finish(PlanNodeStatus.SKIPPED, utc_now()), skipped_reason=SKIPPED_BY_USER)
        writer.save_run(plan_id, skipped_id, finished)
        plan_api_writer().update_node(plan_id, skipped_id, NodeChange(status=PlanNodeStatus.SKIPPED))
    return skipped
