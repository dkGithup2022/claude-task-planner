"""레지스트리 셋: 작업, 조건, 반복 항목."""

from __future__ import annotations

from task_planner.engine.definition.items_source import ItemsSource
from task_planner.engine.definition.run_condition import RunCondition
from task_planner.engine.definition.task.task import Task
from task_planner.engine.registry.in_memory_registry import InMemoryRegistry
from task_planner.engine.registry.registry import Registry

TASKS: Registry[Task] = InMemoryRegistry("작업")


CONDITIONS: Registry[RunCondition] = InMemoryRegistry("조건")


ITEM_SOURCES: Registry[ItemsSource] = InMemoryRegistry("반복 항목")
