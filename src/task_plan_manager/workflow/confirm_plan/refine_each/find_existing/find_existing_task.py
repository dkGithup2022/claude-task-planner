"""find_existing (C 0 단계): 지금 후보와 같은 종류의 기존 지식을 10 개까지 찾는다.
검색어는 후보의 작업 이름과 내용, 페르소나는 계획의 참여 페르소나다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_plan_manager.port.memory_api.memory_api_choice import memory_api_reader
from task_plan_manager.workflow.confirm_plan.refine_each.candidate_kind import memory_kind

SEARCH_LIMIT = 10


@TASKS.register_as("confirm_plan.find_existing")
class FindExistingTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 후보의 종류에 맞는 지식 종류로, 작업 이름과 내용을 검색어로 찾는다
        candidate = context.current_item()
        query = MemorySearchQuery(
            kind=memory_kind(candidate["type"]),
            query=f"{candidate['theme']} {candidate['content']}",
            persona_ids=tuple(context.read("find_plan")["persona_ids"]),
            limit=SEARCH_LIMIT,
        )
        hits = memory_api_reader().search(query)
        existing = [
            {
                "memory_id": hit.memory_id,
                "kind": hit.kind.value,
                "theme": hit.theme,
                "body": hit.body,
                "score": hit.score,
            }
            for hit in hits
        ]
        return TaskOutput({"existing": existing})
