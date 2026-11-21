"""지식을 저장할 때 벡터 검색 켜짐 여부에 따라 벡터를 넘기는지 보는 시험 (DB 없음)."""

from dataclasses import replace
from unittest.mock import ANY, Mock

import pytest

from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.service.memory.dto.memory_create_command import MemoryCreateCommand
from task_plan_server.service.memory.dto.memory_update_command import MemoryUpdateCommand
from task_plan_server.service.memory.impl.default_memory_writer import DefaultMemoryWriter
from task_plan_server.transaction import NoopTransactionManager

EMBEDDING = MemoryEmbedding("fake-model", (0.1, 0.2))
COMMAND = MemoryCreateCommand(
    MemoryKind.PLAN, "문서 작성 계획", "검토를 마지막에 두지 않는다", (1,), ()
)


@pytest.fixture
def repository() -> Mock:
    repository = Mock(spec=MemoryRepository)
    repository.save.side_effect = lambda memory, terms, embedding: replace(memory, memory_id=7)
    return repository


@pytest.fixture
def tokenizer() -> Mock:
    tokenizer = Mock(spec=TextTokenizer)
    tokenizer.tokens.return_value = ("문서",)
    return tokenizer


@pytest.fixture
def embedder() -> Mock:
    embedder = Mock(spec=TextEmbedder)
    embedder.model = "fake-model"
    embedder.embed.return_value = EMBEDDING
    return embedder


@pytest.fixture
def sut(repository: Mock, tokenizer: Mock, embedder: Mock) -> DefaultMemoryWriter:
    return DefaultMemoryWriter(NoopTransactionManager(), repository, tokenizer, embedder)


def test_should_save_without_embedding_when_vector_is_disabled(
    sut: DefaultMemoryWriter, repository: Mock, embedder: Mock
) -> None:
    embedder.enabled = False

    sut.create(COMMAND)

    repository.save.assert_called_once_with(ANY, ANY, None)
    embedder.embed.assert_not_called()


def test_should_save_embedding_of_theme_and_body_when_vector_is_enabled(
    sut: DefaultMemoryWriter, repository: Mock, embedder: Mock
) -> None:
    embedder.enabled = True

    sut.create(COMMAND)

    repository.save.assert_called_once_with(ANY, ANY, EMBEDDING)
    embedder.embed.assert_called_once_with("문서 작성 계획\n검토를 마지막에 두지 않는다")


def test_should_embed_updated_body_when_vector_is_enabled(
    sut: DefaultMemoryWriter, repository: Mock, embedder: Mock
) -> None:
    # given
    embedder.enabled = True
    existing = replace(
        Memory.create(COMMAND.kind, COMMAND.theme, COMMAND.body, (1,), ()), memory_id=7
    )
    repository.find_write_by_id.return_value = existing

    # when
    sut.update(MemoryUpdateCommand(memory_id=7, body="정합성 검증 노드를 따로 두지 않는다"))

    # then
    repository.save.assert_called_once_with(ANY, ANY, EMBEDDING)
    embedder.embed.assert_called_once_with("문서 작성 계획\n정합성 검증 노드를 따로 두지 않는다")
