"""지식 만들기와 고치기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory


class MemoryApiWriter(ABC):
    @abstractmethod
    def create(self, new_memory: NewMemory) -> int:
        """새 지식 (POST /memories). 저장소가 준 memory_id 를 돌려준다."""

    @abstractmethod
    def update(self, memory: Memory) -> int:
        """지식의 본문과 근거를 받은 그대로 저장한다 (PATCH /memories/{memory_id}). 지식이 없으면 MemoryApiError.
        덧붙이기는 부르는 쪽이 읽어서(MemoryApiReader.get) Memory.append 로 덧붙인 뒤 이것으로 저장한다."""
