"""벡터 시험에서 지식을 저장하는 도움 함수. 지식은 repository 로 저장한다 (raw SQL 쓰지 않음)."""

from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_search_terms import MemorySearchTerms
from task_plan_server.persistence.memory.memory_repository import DefaultMemoryRepository

NO_TERMS = MemorySearchTerms(theme=(), body=())


def saved_memory_id(
    repository: DefaultMemoryRepository, theme: str, embedding: MemoryEmbedding | None
) -> int:
    memory = Memory.create(MemoryKind.PLAN, theme, f"{theme} 본문", (1,), ())
    saved = repository.save(memory, NO_TERMS, embedding)
    assert saved.memory_id is not None
    return saved.memory_id
