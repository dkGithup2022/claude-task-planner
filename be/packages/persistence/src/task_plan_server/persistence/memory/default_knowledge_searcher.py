from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam
from task_plan_server.transaction import TransactionManager, transactional

from .memory_entity_query import MemoryEntityQuery
from .text_match_score import query_words, text_match_score


class DefaultKnowledgeSearcher(KnowledgeSearcher):
    """처음 구현: 거른 지식을 글자 맞추기 점수로 줄 세운다 (text_match_score).

    검색어에 낱말이 있으면 점수가 0 보다 큰 것만, 없으면 거른 지식을 고친 시각 최근 순으로 돌려준다.
    """

    def __init__(self, tx: TransactionManager, entities: MemoryEntityQuery) -> None:
        self.tx = tx
        self._entities = entities

    @transactional
    def search_knowledge(self, search_param: SearchParam) -> list[MemorySearchHit]:
        candidates = self._entities.find_for_search_and_active(
            search_param.kind, list(search_param.persona_ids), search_param.theme
        )  # 고친 시각 최근 순
        words = query_words(search_param.query)
        hits = [
            MemorySearchHit(
                entity.id,
                entity.kind,
                entity.theme,
                entity.body,
                text_match_score(words, entity.theme, entity.body),
            )
            for entity in candidates
        ]
        if words:
            hits = [hit for hit in hits if hit.score > 0]
        hits.sort(key=lambda hit: hit.score, reverse=True)  # 같은 점수는 고친 시각 순을 지킨다
        return hits[: max(0, search_param.limit)]
