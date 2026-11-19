"""split_plan: register_plan 이 등록한 계획의 명령서로 노드와 간선을 만들어 계획 저장소에 저장한다.
안에서 네 기능을 차례로 부른다: split_tree(한 층씩 나누기) → write_specs(정의서) → write_edges(간선) → save_graph(저장).
나누기는 몇 번 부를지 실행 전에 모르므로 engine 단계 하나 안에서 우리 코드가 반복한다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.persona.persona import Persona
from task_plan_manager.port.persona_api.persona_api_choice import persona_api_reader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.save_graph.save_graph import save_graph
from task_plan_manager.workflow.make_plan.split_plan.split_tree.split_tree import split_tree
from task_plan_manager.workflow.make_plan.split_plan.write_edges.write_edges import write_edges
from task_plan_manager.workflow.make_plan.split_plan.write_specs.write_specs import write_specs


@TASKS.register_as("make_plan.split_plan")
class SplitPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획의 명령서로 작업 트리 → 정의서 → 간선을 만들고, 계획 저장소에 노드와 간선을 저장한다.
        # 명령서는 계획 저장소에서 읽는다 (요청문의 원본은 API). 호출 기록은 이 단계의 산출물 폴더에 남긴다
        plan = plan_api_reader().get_plan(context.read("register_plan")["plan_id"])
        call_log = PromptCallLog(context.output_dir())
        split = split_tree(plan.title, plan.request, call_log)
        specs = write_specs(plan.request, split.tree, _participants(plan.persona_ids), call_log)
        edges = write_edges(plan.request, specs.drafts, call_log)
        saved = save_graph(plan.plan_id, specs.drafts, edges.edges, plan_api_reader(), plan_api_writer())
        return TaskOutput(
            {
                "node_ids": saved.node_ids,
                "edge_count": saved.edge_count,
                "warnings": [*split.warnings, *specs.warnings, *edges.warnings],
            }
        )


def _participants(persona_ids: tuple[int, ...]) -> tuple[Persona, ...]:
    """페르소나 목록 가운데 계획에 참여한 것만, 계획의 persona_ids 순서대로."""
    by_id = {persona.persona_id: persona for persona in persona_api_reader().list_personas()}
    return tuple(by_id[persona_id] for persona_id in persona_ids if persona_id in by_id)
