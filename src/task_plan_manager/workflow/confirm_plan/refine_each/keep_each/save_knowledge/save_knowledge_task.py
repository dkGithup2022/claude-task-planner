"""save_knowledge: 사용자가 확인한 본문을 지식으로 저장한다. 새로 저장이면 만들기, 덧붙이기면 기존 지식 뒤에 붙이기.
페르소나는 계획의 참여 페르소나 전부, 근거는 후보의 사용자 말마다 (사용자, 2026-11-18)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.memory.memory_source import MemorySource
from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory
from task_plan_manager.port.memory_api.memory_api_choice import memory_api_writer
from task_plan_manager.workflow.confirm_plan.refine_each.candidate_kind import memory_kind
from task_plan_manager.workflow.confirm_plan.refine_each.choose_target.merge_target import merge_target_id


@TASKS.register_as("confirm_plan.save_knowledge")
class SaveKnowledgeTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 저장하지 않기로 했으면 그대로 끝내고, 아니면 새로 만들거나 기존 지식에 덧붙인다
        final = context.read("finalize_knowledge")
        if not final["save"] or not final["body"]:  # 저장하지 않기로 했거나, 덧붙일 내용이 없다
            return TaskOutput({"saved": False, "action": "none", "memory_id": None})
        candidate = context.current_item()
        found = context.read("find_plan")
        sources = tuple(MemorySource(quote=quote, plan_id=found["plan_id"]) for quote in candidate["quotes"])
        target_id = merge_target_id(context)
        if target_id is not None:
            memory_id = memory_api_writer().append(target_id, MemoryAddition(body=final["body"], sources=sources))
            return TaskOutput({"saved": True, "action": "append", "memory_id": memory_id})
        new_memory = NewMemory(
            kind=memory_kind(candidate["type"]),
            theme=final["theme"],
            body=final["body"],
            persona_ids=tuple(found["persona_ids"]),
            sources=sources,
        )
        return TaskOutput({"saved": True, "action": "new", "memory_id": memory_api_writer().create(new_memory)})
