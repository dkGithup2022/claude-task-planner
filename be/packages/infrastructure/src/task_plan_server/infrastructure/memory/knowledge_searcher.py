from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam


class KnowledgeSearcher(ABC):
    """지식 검색 port. 세부 구현(글자, 벡터 등)을 바꿔 끼울 수 있게 따로 둔다."""

    @abstractmethod
    def search_knowledge(
        self, search_param: SearchParam, query_terms: tuple[str, ...]
    ) -> list[MemorySearchHit]:
        """같은 종류이고 페르소나가 하나라도 겹치는 지식을 검색어 낱말과 가까운 순으로 limit 개.

        query_terms 는 검색어를 형태소로 나눈 낱말이다 (search_param.query 는 보지 않는다).
        낱말이 하나라도 맞는 지식만 맞은 정도 순으로. 낱말이 없으면 고친 시각 최근 순.
        theme 을 주면 작업 이름이 같은 것만. 지운 지식은 뺀다. 없으면 [].
        """

    @abstractmethod
    def search_by_embedding(
        self, search_param: SearchParam, embedding: MemoryEmbedding, limit: int
    ) -> list[MemorySearchHit]:
        """거르기는 search_knowledge 와 같고, 같은 모델로 만든 벡터의 지식만 가까운 순으로 limit 개.

        search_param.query 와 search_param.limit 은 보지 않는다. 점수는 코사인 유사도
        (1 - 코사인 거리). 다른 모델로 만든 벡터는 차원이 달라 비교하지 않는다. 없으면 [].
        """
