"""rounds 의 반복 항목: 차례 번호 1 … 노드 수 × 2 + 2.
번호에는 뜻이 없고, 매 차례 run_nodes 가 노드 상태를 다시 읽고 정한다.
차례마다 노드 하나 이상이 끝나거나, 사용자 답 하나가 기록되거나, 30분 마감으로 "계속"이다."""

from __future__ import annotations

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.items_source import ItemsSource
from task_planner.engine.registry.registries import ITEM_SOURCES
from task_planner.port.plan_api.plan_api_choice import plan_api_reader


@ITEM_SOURCES.register_as("plan_run.rounds")
def rounds() -> ItemsSource:
    def items(context: FlowContext) -> list[int]:
        plan = plan_api_reader().get_plan(context.read("find_plan")["plan_id"])
        return list(range(1, len(plan.nodes) * 2 + 3))

    return items
