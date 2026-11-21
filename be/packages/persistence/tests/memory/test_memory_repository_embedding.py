"""지식의 검색용 벡터 저장·비우기·다시 만들 대상 찾기를 실제 Postgres 로 보는 시험."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.persistence.memory.memory_entity import MemoryEntity
from task_plan_server.persistence.memory.memory_repository import DefaultMemoryRepository

from .memory_fixtures import NO_TERMS, saved_memory_id


def _stored_model(session: Session, memory_id: int) -> str | None:
    # 쿼리를 직접 부르므로 트랜잭션을 연다 (session 은 autobegin 을 끈 세이브포인트 모드)
    with session.begin():
        return session.scalar(
            select(MemoryEntity.embedding_model).where(MemoryEntity.id == memory_id)
        )


def _stored_embedding(session: Session, memory_id: int) -> object:
    with session.begin():
        return session.scalar(select(MemoryEntity.embedding).where(MemoryEntity.id == memory_id))


def test_should_clear_embedding_when_saved_with_none(
    session: Session, repository: DefaultMemoryRepository
) -> None:
    # given
    memory_id = saved_memory_id(repository, "문서 작성", MemoryEmbedding("fake-3", (1.0, 0.0, 0.0)))
    assert _stored_model(session, memory_id) == "fake-3"
    memory = repository.find_write_by_id(MemoryIdentity(memory_id))
    assert memory is not None

    # when: 벡터 검색을 끈 상태로 고친다
    repository.save(
        memory.with_update(memory.kind, memory.theme, "새 본문", (1,), ()), NO_TERMS, None
    )
    session.expire_all()

    # then
    assert _stored_model(session, memory_id) is None
    assert _stored_embedding(session, memory_id) is None


def test_should_keep_updated_at_when_embedding_saved(
    session: Session, repository: DefaultMemoryRepository
) -> None:
    # given
    memory_id = saved_memory_id(repository, "API 설계", None)
    before = repository.find_write_by_id(MemoryIdentity(memory_id))
    assert before is not None

    # when
    repository.save_embedding(MemoryIdentity(memory_id), MemoryEmbedding("fake-3", (0.0, 1.0, 0.0)))
    session.expire_all()

    # then
    after = repository.find_write_by_id(MemoryIdentity(memory_id))
    assert after is not None
    assert after.updated_at == before.updated_at
    assert _stored_model(session, memory_id) == "fake-3"


def test_should_find_empty_and_other_model_when_finding_ids_without_embedding(
    repository: DefaultMemoryRepository,
) -> None:
    # given
    empty = saved_memory_id(repository, "벡터 없음", None)
    other = saved_memory_id(repository, "옛 모델", MemoryEmbedding("old-model", (1.0, 0.0)))
    saved_memory_id(repository, "지금 모델", MemoryEmbedding("fake-3", (1.0, 0.0, 0.0)))
    deleted = saved_memory_id(repository, "지운 지식", None)
    repository.delete_by_id(MemoryIdentity(deleted))

    # when
    targets = repository.find_ids_without_embedding_of("fake-3")

    # then
    assert targets == [MemoryIdentity(empty), MemoryIdentity(other)]
