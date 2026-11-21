"""시작할 때 벡터를 다시 만드는 Usecase 시험 (가짜 TextEmbedder, DB 없음)."""

from dataclasses import replace
from unittest.mock import Mock

import pytest

from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.service.memory.usecase.memory_embedding_refresh_usecase import (
    MemoryEmbeddingRefreshUsecase,
)
from task_plan_server.transaction import NoopTransactionManager

EMBEDDING = MemoryEmbedding("fake-model", (0.1, 0.2))


@pytest.fixture
def repository() -> Mock:
    return Mock(spec=MemoryRepository)


@pytest.fixture
def embedder() -> Mock:
    embedder = Mock(spec=TextEmbedder)
    embedder.model = "fake-model"
    embedder.embed.return_value = EMBEDDING
    return embedder


@pytest.fixture
def sut(repository: Mock, embedder: Mock) -> MemoryEmbeddingRefreshUsecase:
    return MemoryEmbeddingRefreshUsecase(NoopTransactionManager(), repository, embedder)


def test_should_do_nothing_when_vector_is_disabled(
    sut: MemoryEmbeddingRefreshUsecase, repository: Mock, embedder: Mock
) -> None:
    embedder.enabled = False

    assert sut.execute() == 0
    repository.find_ids_without_embedding_of.assert_not_called()


def test_should_refill_memories_without_embedding_of_current_model_when_enabled(
    sut: MemoryEmbeddingRefreshUsecase, repository: Mock, embedder: Mock
) -> None:
    # given: 3 은 찾은 뒤에 지워져 없다
    embedder.enabled = True
    memory = replace(Memory.create(MemoryKind.PLAN, "API 설계", "에러 코드", (1,), ()), memory_id=2)
    repository.find_ids_without_embedding_of.return_value = [MemoryIdentity(2), MemoryIdentity(3)]
    repository.find_write_by_id.side_effect = lambda identity: (
        memory if identity.memory_id == 2 else None
    )

    # when
    filled = sut.execute()

    # then
    assert filled == 1
    repository.find_ids_without_embedding_of.assert_called_once_with("fake-model")
    repository.save_embedding.assert_called_once_with(MemoryIdentity(2), EMBEDDING)


def test_execute_is_transactional() -> None:
    assert hasattr(MemoryEmbeddingRefreshUsecase.execute, "__wrapped__")
