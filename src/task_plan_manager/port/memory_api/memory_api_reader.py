"""지식 검색 (POST /memories/search) 과 지식 하나 읽기 (GET /memories/{memory_id})."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery


class MemoryApiReader(ABC):
    @abstractmethod
    def search(self, query: MemorySearchQuery) -> tuple[MemorySearchHit, ...]:
        """점수 높은 순으로 limit 개까지. 없으면 빈 튜플, 서버에서 읽지 못하면 MemoryApiError."""

    @abstractmethod
    def get(self, memory_id: int) -> Memory:
        """지식 하나 (GET /memories/{memory_id}). 없거나 읽지 못하면 MemoryApiError."""
