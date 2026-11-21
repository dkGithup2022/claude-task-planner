"""계획 저장소 구현 고르기. TASK_PLANNER_API=server 면 서버 구현, 아니면 mock."""

from __future__ import annotations

from task_planner.common.http.api_choice import uses_server
from task_planner.port.plan_api.default_plan_api_reader import DefaultPlanApiReader
from task_planner.port.plan_api.default_plan_api_writer import DefaultPlanApiWriter
from task_planner.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_planner.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_planner.port.plan_api.plan_api_reader import PlanApiReader
from task_planner.port.plan_api.plan_api_writer import PlanApiWriter


def plan_api_reader() -> PlanApiReader:
    return DefaultPlanApiReader() if uses_server() else MockPlanApiReader()


def plan_api_writer() -> PlanApiWriter:
    return DefaultPlanApiWriter() if uses_server() else MockPlanApiWriter()
