from dataclasses import replace

from task_plan_server.exception.memory.memory_not_found_exception import MemoryNotFoundException
from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam

from ..dto.memory_list import MemoryList
from ..memory_reader import MemoryReader
from ..search_rank.reciprocal_rank_fusion import reciprocal_rank_fusion
from ..search_terms.query_terms_of import query_terms_of

# 벡터 검색을 켰을 때 전문 검색과 벡터 검색이 각각 가져와 합칠 후보 수.
# 검색 요청의 개수 상한도 30 이라 합친 뒤 앞에서 잘라도 늘 모자라지 않다
CANDIDATE_COUNT = 30


class DefaultMemoryReader(MemoryReader):
    def __init__(
        self,
        repository: MemoryRepository,
        searcher: KnowledgeSearcher,
        tokenizer: TextTokenizer,
        embedder: TextEmbedder,
    ) -> None:
        self._repository = repository
        self._searcher = searcher
        self._tokenizer = tokenizer
        self._embedder = embedder

    def get_by_id(self, identity: MemoryIdentity) -> MemoryRead:
        read = self._repository.find_by_id(identity)
        if read is None:
            raise MemoryNotFoundException(f"memory not found: {identity.memory_id}")
        return read

    def search(self, search_param: SearchParam) -> list[MemorySearchHit]:
        # 검색어를 저장할 때와 같은 규칙으로 낱말로 나눈다. 낱말이 없으면 (검색어가 비었거나
        # 숫자, 기호, 조사만 있음) 맞는 지식이 없으므로 벡터 검색을 켜도 빈 결과다
        query_terms = query_terms_of(self._tokenizer, search_param.query)
        if not query_terms:
            return []
        if not self._embedder.enabled:
            return self._full_text_search(search_param, query_terms)
        return self._hybrid_search(search_param, query_terms)

    def get_list(self, condition: MemoryListCondition) -> MemoryList:
        items = self._repository.find_by_condition(condition)
        return MemoryList(tuple(items), self._repository.count_by_condition(condition))

    def _full_text_search(
        self, search_param: SearchParam, query_terms: tuple[str, ...]
    ) -> list[MemorySearchHit]:
        """형태소 낱말로 찾는다."""
        return self._searcher.search_knowledge(search_param, query_terms)

    def _hybrid_search(
        self, search_param: SearchParam, query_terms: tuple[str, ...]
    ) -> list[MemorySearchHit]:
        """전문 검색과 벡터 검색에서 각각 후보를 가져와 RRF 로 합친 뒤 앞에서 limit 개."""
        text_hits = self._full_text_search(
            replace(search_param, limit=CANDIDATE_COUNT), query_terms
        )
        query_embedding = self._embedder.embed(search_param.query)
        vector_hits = self._searcher.search_by_embedding(
            search_param, query_embedding, CANDIDATE_COUNT
        )
        return reciprocal_rank_fusion(text_hits, vector_hits)[: search_param.limit]
