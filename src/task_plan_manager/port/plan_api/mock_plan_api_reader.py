"""계획 저장소 읽기의 mock 구현. .mockData/ 의 파일에서 읽는다."""

from __future__ import annotations

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.port.plan_api.mock_plan_files import load_plan
from task_plan_manager.port.plan_api.plan_api_reader import PlanApiReader


class MockPlanApiReader(PlanApiReader):
    def get_plan(self, plan_id: int) -> Plan:
        # .mockData/plans/<plan_id>.json 을 읽어 노드·간선까지 담은 계획으로 돌려준다
        return load_plan(plan_id)
