"""지식 읽기의 mock 구현. 검색은 검색어와 상관없이 정해진 결과를 돌려준다 (사용자, 2026-11-19)."""

from __future__ import annotations

from task_planner.model.memory.memory import Memory
from task_planner.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_planner.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.port.memory_api.memory_api_reader import MemoryApiReader
from task_planner.port.memory_api.mock_memory_files import load_memories


class MockMemoryApiReader(MemoryApiReader):
    def search(self, query: MemorySearchQuery) -> tuple[MemorySearchHit, ...]:
        # mock 에 저장된 지식을 저장된 순서대로 limit 개까지, 점수는 모두 1.0 으로 돌려준다
        return tuple(
            MemorySearchHit(memory.memory_id, memory.kind, memory.theme, memory.body, score=1.0)
            for memory in load_memories()[: query.limit]
        )

    def get(self, memory_id: int) -> Memory:
        # mock 파일에서 그 지식을 찾는다
        found = next((memory for memory in load_memories() if memory.memory_id == memory_id), None)
        if found is None:
            raise MemoryApiError(f"지식 {memory_id} 가 mock 에 없습니다")
        return found
