"""refine_each 의 반복 항목: extract_knowledge 가 남긴 지식 후보 목록 (16 개까지 이미 잘려 있다)."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.items_source import ItemsSource
from task_planner.engine.registry.registries import ITEM_SOURCES


@ITEM_SOURCES.register_as("confirm_plan.candidates")
def candidates() -> ItemsSource:
    def items(context: FlowContext) -> list[dict[str, Any]]:
        return list(context.read("extract_knowledge")["candidates"])

    return items
