from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.model.memory.memory_search_terms import MemorySearchTerms


class MemoryRepository(ABC):
    @abstractmethod
    def save(self, memory: Memory, terms: MemorySearchTerms) -> Memory:
        """지식 저장 (신규·수정). 페르소나와 근거의 순서를 지킨다. 검색용 낱말도 같이 저장한다.

        저장한 지식을 돌려준다.
        """

    @abstractmethod
    def save_search_terms(self, identity: MemoryIdentity, terms: MemorySearchTerms) -> None:
        """검색용 낱말만 바꾼다. 고친 시각은 그대로. 지운 지식이면 no-op."""

    @abstractmethod
    def find_ids_without_search_terms(self) -> list[MemoryIdentity]:
        """검색용 낱말이 비어 있는 지식 (지운 것 뺌). 직접 넣은 데이터를 채울 때 쓴다. 없으면 []."""

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
