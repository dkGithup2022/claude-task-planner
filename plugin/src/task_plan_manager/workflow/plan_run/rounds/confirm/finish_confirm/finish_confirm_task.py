"""finish_confirm (D 4): 허가면 확인 노드의 result.md 와 run.json(사용자가 한 말)을 쓰고 완료로.
허가하지 않으면 멈춘다. 어떻게 할지는 흐름 밖에서 대화로 정한다 (사용자, 2026-11-18).
result.md 모양은 기존 run.py:235-260 (confirm) 에서 노드 스펙 사본 절을 뺀 것."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.common.clock import utc_now
from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.workflow.plan_run.rounds.confirm.confirm_choices import ALLOW
from task_plan_manager.workflow.plan_run.rounds.save_stop import CONFIRM_DENIED, again_line, save_stop

NO_WORDS = "(말하지 않음)"


@TASKS.register_as("plan_run.finish_confirm")
class FinishConfirmTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        plan = plan_api_reader().get_plan(context.read("find_plan")["plan_id"])
        stopped = context.read("run_nodes")
        node_id = int(stopped["node_id"])
        if context.read("ask_confirm")["answer"] != ALLOW:
            title = plan.node(node_id).title
            message = (
                f'노드 {node_id} "{title}" 을 허가하지 않아 멈췄습니다. '
                f"어떻게 할지 말씀해 주세요. {again_line(plan.plan_id)}"
            )
            save_stop(context, plan.plan_id, CONFIRM_DENIED, node_id, message)
            return TaskOutput({"allowed": False})
        talk = context.read("show_confirm")
        words = _user_words(talk.get("transcript"), stopped["finished_at"], talk["to"])
        _record_confirmed(plan, node_id, words)
        return TaskOutput({"allowed": True})


def _user_words(transcript: str | None, start: str, end: str) -> str:
    """확인 대화 구간(run_nodes 가 돌아온 때부터 대화가 끝난 때까지)의 사용자 말."""
    if not transcript or not Path(transcript).exists():
        return NO_WORDS
    lines = [
        u.text.strip() for u in dialogue(Path(transcript), until=end) if u.role == "user" and u.at[:19] >= start[:19]
    ]
    return "\n".join(line for line in lines if line) or NO_WORDS


def _record_confirmed(plan: Plan, node_id: int, words: str) -> None:
    """확인 노드의 result.md, run.json(완료, 사용자가 한 말), 노드 상태 done."""
    node = plan.node(node_id)
    previous = [plan.node(pre_id) for pre_id in plan.prerequisites(node_id)]
    folder = DefaultPlanFolderReader()
    checked = []
    for pre in previous:
        output = folder.read_output(plan.plan_id, pre.node_id)
        where = str(output.result_path) if output else "결과 없음"
        checked.append(f'- 노드 {pre.node_id} "{pre.title}": {where}')
    body = [
        f"# 확인: {node.title}",
        "",
        "사용자가 확인하고 다음으로 넘어가도 된다고 허가했다.",
        "",
        "## 사용자가 한 말",
        words,
        "",
        "## 확인한 앞 노드 결과",
        *checked,
    ]
    writer = DefaultPlanFolderWriter()
    writer.write_result(plan.plan_id, node_id, "\n".join(body) + "\n")
    run = folder.read_run(plan.plan_id, node_id) or NodeRun(round=1, status=PlanNodeStatus.TODO)
    writer.save_run(plan.plan_id, node_id, replace(run.finish(PlanNodeStatus.DONE, utc_now()), confirm=words))
    plan_api_writer().update_node(plan.plan_id, node_id, NodeChange(status=PlanNodeStatus.DONE))
