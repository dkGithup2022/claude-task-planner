"""벡터 검색 (search_by_embedding) 을 실제 Postgres(pgvector) 에 손으로 만든 벡터로 보는 시험."""

from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.search_param import SearchParam
from task_plan_server.persistence.memory.default_knowledge_searcher import DefaultKnowledgeSearcher
from task_plan_server.persistence.memory.memory_repository import DefaultMemoryRepository

from .memory_fixtures import saved_memory_id

PARAM = SearchParam(MemoryKind.PLAN, "아무 글", (1,))


def test_should_order_by_cosine_similarity_when_searched_by_embedding(
    repository: DefaultMemoryRepository, searcher: DefaultKnowledgeSearcher
) -> None:
    # given
    near = saved_memory_id(repository, "문서 작성 계획", MemoryEmbedding("fake-3", (0.9, 0.1, 0.0)))
    far = saved_memory_id(repository, "API 서버 개발", MemoryEmbedding("fake-3", (0.1, 0.9, 0.0)))
    saved_memory_id(repository, "벡터 없음", None)

    # when
    hits = searcher.search_by_embedding(PARAM, MemoryEmbedding("fake-3", (0.8, 0.2, 0.0)), 30)

    # then: 벡터가 없는 지식은 나오지 않고, 점수는 1 - 코사인 거리
    assert [hit.memory_id for hit in hits] == [near, far]
    assert 0.99 < hits[0].score <= 1
    assert hits[1].score < hits[0].score


def test_should_compare_only_same_model_when_other_dimension_is_mixed(
    repository: DefaultMemoryRepository, searcher: DefaultKnowledgeSearcher
) -> None:
    # given: 다른 모델(다른 차원) 로 만든 벡터가 같은 테이블에 섞여 있다
    same = saved_memory_id(repository, "문서 작성 계획", MemoryEmbedding("fake-3", (0.9, 0.1, 0.0)))
    saved_memory_id(repository, "테이블 설계", MemoryEmbedding("fake-4", (0.2, 0.3, 0.9, 0.1)))

    # when: 차원이 다른 벡터를 비교하면 쿼리 전체가 실패하므로, 에러 없이 끝나는지가 핵심이다
    hits = searcher.search_by_embedding(PARAM, MemoryEmbedding("fake-3", (0.8, 0.2, 0.0)), 30)

    # then
    assert [hit.memory_id for hit in hits] == [same]


def test_should_limit_and_skip_other_persona_when_searched_by_embedding(
    repository: DefaultMemoryRepository, searcher: DefaultKnowledgeSearcher
) -> None:
    # given
    first = saved_memory_id(repository, "첫째", MemoryEmbedding("fake-3", (1.0, 0.0, 0.0)))
    saved_memory_id(repository, "둘째", MemoryEmbedding("fake-3", (0.5, 0.5, 0.0)))
    other_persona = SearchParam(MemoryKind.PLAN, "아무 글", (2,))

    # when
    limited = searcher.search_by_embedding(PARAM, MemoryEmbedding("fake-3", (1.0, 0.0, 0.0)), 1)
    other = searcher.search_by_embedding(
        other_persona, MemoryEmbedding("fake-3", (1.0, 0.0, 0.0)), 30
    )

    # then
    assert [hit.memory_id for hit in limited] == [first]
    assert other == []
