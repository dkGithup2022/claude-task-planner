from dataclasses import dataclass

from task_plan_server.model.memory.memory_read import MemoryRead


@dataclass(frozen=True, slots=True)
class MemoryList:
    """웹 지식 목록. total 은 limit 을 빼고 조건에 맞는 개수."""

    items: tuple[MemoryRead, ...]
    total: int
