from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead


class MemoryRepository(ABC):
    @abstractmethod
    def save(self, memory: Memory) -> Memory:
        """지식 저장 (신규·수정). 페르소나와 근거의 순서를 지킨다. 저장한 지식을 돌려준다."""

    @abstractmethod
    def find_write_by_id(self, identity: MemoryIdentity) -> Memory | None:
        """지식 Write 모델 조회. 지운 지식은 없음으로 본다."""

    @abstractmethod
    def find_by_id(self, identity: MemoryIdentity) -> MemoryRead | None:
        """지식 조회 (덧붙인 횟수, 근거 계획 포함). 지운 지식은 없음으로 본다."""

    @abstractmethod
    def delete_by_id(self, identity: MemoryIdentity) -> None:
        """지식 soft-delete. 이미 지웠으면 no-op."""

    @abstractmethod
    def find_by_condition(self, condition: MemoryListCondition) -> list[MemoryRead]:
        """조건에 맞는 지식을 고친 시각 최근 순으로 limit 개. 지운 지식은 뺀다. 없으면 []."""

    @abstractmethod
    def count_by_condition(self, condition: MemoryListCondition) -> int:
        """조건에 맞는 지식 수. limit 은 보지 않는다."""
