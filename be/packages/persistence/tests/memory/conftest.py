import pytest
from sqlalchemy.orm import Session

from task_plan_server.persistence.memory.default_knowledge_searcher import DefaultKnowledgeSearcher
from task_plan_server.persistence.memory.memory_entity_query import MemoryEntityQuery
from task_plan_server.persistence.memory.memory_repository import DefaultMemoryRepository
from task_plan_server.persistence.transaction import DefaultTransactionManager


@pytest.fixture
def repository(session: Session) -> DefaultMemoryRepository:
    return DefaultMemoryRepository(DefaultTransactionManager(session), MemoryEntityQuery(session))


@pytest.fixture
def searcher(session: Session) -> DefaultKnowledgeSearcher:
    return DefaultKnowledgeSearcher(DefaultTransactionManager(session), MemoryEntityQuery(session))
