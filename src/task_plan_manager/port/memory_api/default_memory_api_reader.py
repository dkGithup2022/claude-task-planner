"""지식 검색의 서버 구현. POST {서버 주소}/memories/search."""

from __future__ import annotations

from task_plan_manager.common.http.api_choice import api_url
from task_plan_manager.common.http.http_json import request_json
from task_plan_manager.common.http.http_json_error import HttpJsonError
from task_plan_manager.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_plan_manager.port.memory_api.memory_api_converter import MemoryApiConverter
from task_plan_manager.port.memory_api.memory_api_error import MemoryApiError
from task_plan_manager.port.memory_api.memory_api_reader import MemoryApiReader


class DefaultMemoryApiReader(MemoryApiReader):
    def search(self, query: MemorySearchQuery) -> tuple[MemorySearchHit, ...]:
        # 검색 요청을 보내고 응답의 items 를 검색 결과로 바꾼다
        converter = MemoryApiConverter()
        try:
            body = request_json("POST", api_url("/memories/search"), converter.to_search_body(query))
        except HttpJsonError as failed:
            raise MemoryApiError(str(failed)) from failed
        return converter.to_search_hits(body)
