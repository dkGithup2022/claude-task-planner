from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam
from task_plan_server.transaction import TransactionManager, transactional

from .memory_entity import MemoryEntity
from .memory_entity_query import MemoryEntityQuery


class DefaultKnowledgeSearcher(KnowledgeSearcher):
    """한국어 형태소 기반 전문 검색 (2026-11-21).

    search_tokens (tsvector) 에 검색어 낱말이 하나라도 맞는 지식을 ts_rank 점수 순으로 돌려준다.
    낱말이 없으면 (검색어가 빔) 거른 지식을 고친 시각 최근 순으로,
    점수 0 으로 돌려준다.
    """

    def __init__(self, tx: TransactionManager, entities: MemoryEntityQuery) -> None:
        self.tx = tx
        self._entities = entities

    @transactional
    def search_knowledge(
        self, search_param: SearchParam, query_terms: tuple[str, ...]
    ) -> list[MemorySearchHit]:
        persona_ids = list(search_param.persona_ids)
        if not query_terms:
            candidates = self._entities.find_for_search_and_active(
                search_param.kind, persona_ids, search_param.theme
            )  # 고친 시각 최근 순
            return [_hit(entity, 0.0) for entity in candidates[: max(0, search_param.limit)]]
        ranked = self._entities.find_for_search_by_terms_and_active(
            search_param.kind, persona_ids, search_param.theme, query_terms, search_param.limit
        )
        return [_hit(entity, score) for entity, score in ranked]


def _hit(entity: MemoryEntity, score: float) -> MemorySearchHit:
    return MemorySearchHit(entity.id, entity.kind, entity.theme, entity.body, score)
