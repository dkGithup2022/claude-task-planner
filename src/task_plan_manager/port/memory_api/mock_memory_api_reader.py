"""지식 검색의 mock 구현. 검색어와 상관없이 정해진 결과를 돌려준다 (사용자, 2026-11-19)."""

from __future__ import annotations

from task_plan_manager.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_plan_manager.port.memory_api.memory_api_reader import MemoryApiReader
from task_plan_manager.port.memory_api.mock_memory_files import load_memories


class MockMemoryApiReader(MemoryApiReader):
    def search(self, query: MemorySearchQuery) -> tuple[MemorySearchHit, ...]:
        # mock 에 저장된 지식을 저장된 순서대로 limit 개까지, 점수는 모두 1.0 으로 돌려준다
        return tuple(
            MemorySearchHit(memory.memory_id, memory.kind, memory.theme, memory.body, score=1.0)
            for memory in load_memories()[: query.limit]
        )
