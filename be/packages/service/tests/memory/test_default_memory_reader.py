"""지식 검색이 벡터 검색 켜짐 여부로 나뉘는지 보는 시험 (가짜 TextEmbedder, DB 없음)."""

from unittest.mock import Mock

import pytest

from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.model.memory.search_param import SearchParam
from task_plan_server.service.memory.impl.default_memory_reader import (
    CANDIDATE_COUNT,
    DefaultMemoryReader,
)

QUERY_EMBEDDING = MemoryEmbedding("fake-model", (0.1, 0.2, 0.3))


def _hit(memory_id: int) -> MemorySearchHit:
    return MemorySearchHit(memory_id, MemoryKind.PLAN, f"작업 {memory_id}", "본문", 0.5)


def _param(query: str = "문서 검토", limit: int = 2) -> SearchParam:
    return SearchParam(MemoryKind.PLAN, query, (1,), limit=limit)


@pytest.fixture
def searcher() -> Mock:
    return Mock(spec=KnowledgeSearcher)


@pytest.fixture
def tokenizer() -> Mock:
    tokenizer = Mock(spec=TextTokenizer)
    tokenizer.tokens.side_effect = lambda text: tuple(text.split()) if text.strip() else ()
    return tokenizer


@pytest.fixture
def embedder() -> Mock:
    embedder = Mock(spec=TextEmbedder)
    embedder.model = "fake-model"
    embedder.embed.return_value = QUERY_EMBEDDING
    return embedder


@pytest.fixture
def sut(searcher: Mock, tokenizer: Mock, embedder: Mock) -> DefaultMemoryReader:
    return DefaultMemoryReader(Mock(spec=MemoryRepository), searcher, tokenizer, embedder)


def test_should_use_full_text_only_when_vector_is_disabled(
    sut: DefaultMemoryReader, searcher: Mock, embedder: Mock
) -> None:
    # given
    embedder.enabled = False
    searcher.search_knowledge.return_value = [_hit(1)]

    # when
    hits = sut.search(_param())

    # then
    assert hits == [_hit(1)]
    searcher.search_knowledge.assert_called_once_with(_param(), ("문서", "검토"))
    searcher.search_by_embedding.assert_not_called()
    embedder.embed.assert_not_called()


def test_should_merge_full_text_and_vector_when_vector_is_enabled(
    sut: DefaultMemoryReader, searcher: Mock, embedder: Mock
) -> None:
    # given: 2 는 두 검색 모두에 나온다
    embedder.enabled = True
    searcher.search_knowledge.return_value = [_hit(1), _hit(2)]
    searcher.search_by_embedding.return_value = [_hit(3), _hit(2)]

    # when
    hits = sut.search(_param(limit=2))

    # then: 후보는 각각 30 개씩, 합친 뒤 앞에서 limit 개
    assert [hit.memory_id for hit in hits] == [2, 1]
    searcher.search_knowledge.assert_called_once_with(
        _param(limit=CANDIDATE_COUNT), ("문서", "검토")
    )
    searcher.search_by_embedding.assert_called_once_with(
        _param(limit=2), QUERY_EMBEDDING, CANDIDATE_COUNT
    )
    embedder.embed.assert_called_once_with("문서 검토")


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("query", ["", "404"])
def test_should_return_empty_when_query_has_no_terms(
    sut: DefaultMemoryReader,
    searcher: Mock,
    tokenizer: Mock,
    embedder: Mock,
    enabled: bool,
    query: str,
) -> None:
    # given: 검색어가 비었거나 낱말이 남지 않는 검색어 (숫자만)
    embedder.enabled = enabled
    tokenizer.tokens.side_effect = lambda text: ()

    # when
    hits = sut.search(_param(query=query))

    # then: 벡터 검색을 켜도 찾지 않는다
    assert hits == []
    searcher.search_knowledge.assert_not_called()
    searcher.search_by_embedding.assert_not_called()
    embedder.embed.assert_not_called()
