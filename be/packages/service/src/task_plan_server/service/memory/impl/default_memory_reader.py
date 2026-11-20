from task_plan_server.exception.memory.memory_not_found_exception import MemoryNotFoundException
from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_read import MemoryRead
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam

from ..dto.memory_list import MemoryList
from ..memory_reader import MemoryReader


class DefaultMemoryReader(MemoryReader):
    def __init__(self, repository: MemoryRepository, searcher: KnowledgeSearcher) -> None:
        self._repository = repository
        self._searcher = searcher

    def get_by_id(self, identity: MemoryIdentity) -> MemoryRead:
        read = self._repository.find_by_id(identity)
        if read is None:
            raise MemoryNotFoundException(f"memory not found: {identity.memory_id}")
        return read

    def search(self, search_param: SearchParam) -> list[MemorySearchHit]:
        return self._searcher.search_knowledge(search_param)

    def get_list(self, condition: MemoryListCondition) -> MemoryList:
        items = self._repository.find_by_condition(condition)
        return MemoryList(tuple(items), self._repository.count_by_condition(condition))
