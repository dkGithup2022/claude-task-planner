"""지식 만들기·덧붙이기의 서버 구현. POST {서버 주소}/memories, /memories/{memory_id}/append."""

from __future__ import annotations

from typing import Any

from task_plan_manager.common.http.api_choice import api_url
from task_plan_manager.common.http.http_json import request_json
from task_plan_manager.common.http.http_json_error import HttpJsonError
from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory
from task_plan_manager.port.memory_api.memory_api_converter import MemoryApiConverter
from task_plan_manager.port.memory_api.memory_api_error import MemoryApiError
from task_plan_manager.port.memory_api.memory_api_writer import MemoryApiWriter


class DefaultMemoryApiWriter(MemoryApiWriter):
    def create(self, new_memory: NewMemory) -> int:
        # 새 지식을 보내고 서버가 준 memory_id 를 돌려준다
        converter = MemoryApiConverter()
        return converter.to_memory_id(_post("/memories", converter.to_create_body(new_memory)))

    def append(self, memory_id: int, addition: MemoryAddition) -> int:
        # 덧붙일 본문과 근거를 보내고 서버가 준 memory_id 를 돌려준다
        converter = MemoryApiConverter()
        return converter.to_memory_id(_post(f"/memories/{memory_id}/append", converter.to_append_body(addition)))


def _post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        return dict(request_json("POST", api_url(path), body))
    except HttpJsonError as failed:
        raise MemoryApiError(str(failed)) from failed
