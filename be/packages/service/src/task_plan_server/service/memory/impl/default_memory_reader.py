from task_plan_server.exception.memory.memory_not_found_exception import MemoryNotFoundException
from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam

from ..dto.memory_list import MemoryList
from ..memory_reader import MemoryReader
from ..search_terms.query_terms_of import query_terms_of


class DefaultMemoryReader(MemoryReader):
    def __init__(
        self, repository: MemoryRepository, searcher: KnowledgeSearcher, tokenizer: TextTokenizer
    ) -> None:
        self._repository = repository
        self._searcher = searcher
        self._tokenizer = tokenizer

    def get_by_id(self, identity: MemoryIdentity) -> MemoryRead:
        read = self._repository.find_by_id(identity)
        if read is None:
            raise MemoryNotFoundException(f"memory not found: {identity.memory_id}")
        return read

    def search(self, search_param: SearchParam) -> list[MemorySearchHit]:
        # 검색어를 저장할 때와 같은 규칙으로 낱말로 나눠 넘긴다
        query_terms = query_terms_of(self._tokenizer, search_param.query)
        if _has_text_but_no_terms(search_param.query, query_terms):
            return []
        return self._searcher.search_knowledge(search_param, query_terms)

    def get_list(self, condition: MemoryListCondition) -> MemoryList:
        items = self._repository.find_by_condition(condition)
        return MemoryList(tuple(items), self._repository.count_by_condition(condition))


def _has_text_but_no_terms(query: str, query_terms: tuple[str, ...]) -> bool:
    """검색어에 글자는 있는데 낱말이 하나도 남지 않았는지 (숫자, 기호, 조사만 있는 검색어).

    이때 최근 지식을 돌려주면 관계없는 지식이 검색 결과처럼 보이므로 빈 결과로 둔다.
    """
    return bool(query.strip()) and not query_terms
