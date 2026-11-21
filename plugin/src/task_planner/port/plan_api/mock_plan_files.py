"""mock 계획 파일을 읽고 쓰는 함수. mock 읽기·쓰기 구현이 같이 쓴다."""

from __future__ import annotations

from task_planner.common import files
from task_planner.model.plan.plan import Plan
from task_planner.port.plan_api.mock_plan_location import plan_file
from task_planner.port.plan_api.plan_json_converter import PlanJsonConverter
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError


def load_plan(plan_id: int) -> Plan:
    plan_path = plan_file(plan_id)
    if not plan_path.exists():
        raise PlanNotFoundError(f"계획 {plan_id} 가 mock 저장소에 없습니다 ({plan_path})")
    return PlanJsonConverter().to_plan(files.read_json(plan_path))


def save_plan(plan: Plan) -> None:
    files.write_json(plan_file(plan.plan_id), PlanJsonConverter().to_body(plan))
