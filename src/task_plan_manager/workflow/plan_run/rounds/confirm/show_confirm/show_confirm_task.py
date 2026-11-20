"""show_confirm (D 4): 메인 세션이 확인 노드의 작업 지시대로 앞 노드 결과에서 확인할 부분을 골라 보이고 질문에 답한다.
넘어가도 되는지는 다음 단계(ask_confirm)가 묻는다 (사용자, 2026-11-20 "나로 고고", 기존 plan-run SKILL.md:35)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.conversation_request import ConversationRequest
from task_plan_manager.port.local.plan_folder.plan_folder_location import prompt_file
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.plan_run.rounds.run_nodes.node_run_input import previous_results


@TASKS.register_as("plan_run.show_confirm")
class ShowConfirmTask(Task):
    request_type = ConversationRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ConversationRequest:
        plan = plan_api_reader().get_plan(context.read("find_plan")["plan_id"])
        node = plan.node(int(context.read("run_nodes")["node_id"]))
        prompt_path = prompt_file(plan.plan_id, node.node_id).resolve()
        goal = (
            f'확인 노드 {node.node_id} "{node.title}" 의 작업 지시 {prompt_path} 를 읽고, '
            "거기 적힌 대로 아래 앞 노드 결과에서 사용자가 확인할 부분만 골라 보인다. 사용자의 질문에 답한다. "
            "질문이 없으면 바로 끝낸다. 넘어가도 되는지는 묻지 않는다 (다음 단계가 묻는다).\n"
            f"{previous_results(plan, node.node_id)}"
        )
        opening = f'노드 {node.node_id} "{node.title}" 을 확인할 차례입니다. 확인하실 부분을 모아 보여 드리겠습니다.'
        return ConversationRequest(goal=goal, opening=opening)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput(dict(result))  # {from, to, transcript}
