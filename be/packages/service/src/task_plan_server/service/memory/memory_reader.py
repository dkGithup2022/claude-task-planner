from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam

from .dto.memory_list import MemoryList


class MemoryReader(ABC):
    @abstractmethod
    def get_by_id(self, identity: MemoryIdentity) -> MemoryRead:
        """지식 하나. 없으면 MemoryNotFoundException."""

    @abstractmethod
    def search(self, search_param: SearchParam) -> list[MemorySearchHit]:
        """지식 검색. 점수 높은 순으로 limit 개. 없으면 []."""

    @abstractmethod
    def get_list(self, condition: MemoryListCondition) -> MemoryList:
        """웹 지식 목록. 고친 시각 최근 순."""
