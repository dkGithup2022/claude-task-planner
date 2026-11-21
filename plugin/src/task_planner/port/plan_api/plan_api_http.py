"""계획 저장소 서버 구현이 같이 쓰는 호출. 서버 실패는 PlanApiError, 404 는 PlanNotFoundError 로 바꾼다."""

from __future__ import annotations

from typing import Any

from task_planner.common.http.api_choice import api_url
from task_planner.common.http.http_json import request_json
from task_planner.common.http.http_json_error import HttpJsonError
from task_planner.port.plan_api.plan_api_error import PlanApiError
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError


def call_plan_api(method: str, path: str, body: Any = None) -> Any:
    try:
        return request_json(method, api_url(path), body)
    except HttpJsonError as failed:
        if "(404)" in str(failed):
            raise PlanNotFoundError(str(failed)) from failed
        raise PlanApiError(str(failed)) from failed
