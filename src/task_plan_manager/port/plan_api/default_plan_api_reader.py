"""계획 저장소 읽기의 서버 구현. GET {서버 주소}/plans/{plan_id}."""

from __future__ import annotations

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.port.plan_api.plan_api_http import call_plan_api
from task_plan_manager.port.plan_api.plan_api_reader import PlanApiReader
from task_plan_manager.port.plan_api.plan_json_converter import PlanJsonConverter


class DefaultPlanApiReader(PlanApiReader):
    def get_plan(self, plan_id: int) -> Plan:
        # 노드와 간선까지 담긴 계획 응답을 Plan 으로 바꾼다. 없으면 PlanNotFoundError
        return PlanJsonConverter().to_plan(call_plan_api("GET", f"/plans/{plan_id}"))
