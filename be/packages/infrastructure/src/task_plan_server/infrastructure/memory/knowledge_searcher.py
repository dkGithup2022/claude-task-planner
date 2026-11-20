from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam


class KnowledgeSearcher(ABC):
    """지식 검색 port. 세부 구현(글자, 벡터 등)을 바꿔 끼울 수 있게 따로 둔다."""

    @abstractmethod
    def search_knowledge(self, search_param: SearchParam) -> list[MemorySearchHit]:
        """같은 종류이고 페르소나가 하나라도 겹치는 지식을 검색어와 가까운 순으로 limit 개.

        theme 을 주면 작업 이름이 같은 것만. 지운 지식은 뺀다. 없으면 [].
        """
