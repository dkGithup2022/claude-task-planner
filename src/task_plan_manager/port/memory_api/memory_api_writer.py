"""지식 만들기와 덧붙이기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory


class MemoryApiWriter(ABC):
    @abstractmethod
    def create(self, new_memory: NewMemory) -> int:
        """새 지식 (POST /memories). 저장소가 준 memory_id 를 돌려준다."""

    @abstractmethod
    def append(self, memory_id: int, addition: MemoryAddition) -> int:
        """기존 지식의 본문과 근거 뒤에 덧붙인다 (POST /memories/{memory_id}/append). 지식이 없으면 MemoryApiError."""
