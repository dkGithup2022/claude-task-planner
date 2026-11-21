"""find_existing (C 0 단계): 지금 후보와 같은 종류의 기존 지식을 10 개까지 찾는다.
검색어는 후보의 작업 이름과 내용, 페르소나는 계획의 참여 페르소나다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_planner.port.memory_api.memory_api_choice import memory_api_reader
from task_planner.workflow.confirm_plan.refine_each.candidate_kind import memory_kind
from task_planner.workflow.confirm_plan.refine_each.find_existing.search_word import build_search_word

SEARCH_LIMIT = 10  # 바꾸면 choose_target 쪽 수(선언의 단계 셋)도 맞춘다. 시험이 지킨다


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
            query=build_search_word(candidate),
            persona_ids=tuple(context.read("find_plan")["persona_ids"]),
            limit=SEARCH_LIMIT,
        )
        hits = memory_api_reader().search(query)[:SEARCH_LIMIT]  # 고르기 쪽은 이 수에 맞춰 셋이다
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
