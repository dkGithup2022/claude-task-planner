"""지식 만들기·고치기의 서버 구현. POST {서버 주소}/memories, PATCH {서버 주소}/memories/{memory_id}."""

from __future__ import annotations

from typing import Any

from task_planner.common.http.api_choice import api_url
from task_planner.common.http.http_json import request_json
from task_planner.common.http.http_json_error import HttpJsonError
from task_planner.model.memory.memory import Memory
from task_planner.port.memory_api.dto.new_memory import NewMemory
from task_planner.port.memory_api.memory_api_converter import MemoryApiConverter
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.port.memory_api.memory_api_writer import MemoryApiWriter


class DefaultMemoryApiWriter(MemoryApiWriter):
    def create(self, new_memory: NewMemory) -> int:
        # 새 지식을 보내고 서버가 준 memory_id 를 돌려준다
        converter = MemoryApiConverter()
        return converter.to_memory_id(_post("/memories", converter.to_create_body(new_memory)))

    def update(self, memory: Memory) -> int:
        # 본문과 근거 전체를 보내고 서버가 준 memory_id 를 돌려준다
        converter = MemoryApiConverter()
        path = f"/memories/{memory.memory_id}"
        return converter.to_memory_id(_send("PATCH", path, converter.to_update_body(memory)))


def _post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    return _send("POST", path, body)


def _send(method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        return dict(request_json(method, api_url(path), body))
    except HttpJsonError as failed:
        raise MemoryApiError(str(failed)) from failed
