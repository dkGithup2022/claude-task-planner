import pytest

from task_plan_manager.model.memory.memory_kind import MemoryKind
from task_plan_manager.model.memory.memory_source import MemorySource
from task_plan_manager.port.memory_api.default_memory_api_reader import DefaultMemoryApiReader
from task_plan_manager.port.memory_api.default_memory_api_writer import DefaultMemoryApiWriter
from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory
from task_plan_manager.port.memory_api.memory_api_error import MemoryApiError
from task_plan_manager.port.memory_api.mock_memory_api_reader import MockMemoryApiReader
from task_plan_manager.port.memory_api.mock_memory_api_writer import MockMemoryApiWriter
from task_plan_manager.port.memory_api.mock_memory_files import load_memories

QUERY = MemorySearchQuery(MemoryKind.KNOWLEDGE, "아무 검색어", (1,), limit=10)
NEW = NewMemory(MemoryKind.KNOWLEDGE, "API 설계", "목록은 페이지로 나눈다", (1,), (MemorySource("페이지로", 3),))


def test_should_return_fixed_results_from_mock_regardless_of_query():
    hits = MockMemoryApiReader().search(QUERY)
    other = MockMemoryApiReader().search(MemorySearchQuery(MemoryKind.PLAN, "전혀 다른 말", (2,), limit=1))
    assert [hit.memory_id for hit in hits] == [1, 2] and all(hit.score == 1.0 for hit in hits)
    assert [hit.memory_id for hit in other] == [1]  # limit 만 따른다


def test_should_create_and_append_in_mock():
    writer = MockMemoryApiWriter()
    memory_id = writer.create(NEW)
    assert memory_id == 3
    assert writer.append(2, MemoryAddition("FK 는 기존을 따른다", (MemorySource("fk", 1),))) == 2

    memories = {memory.memory_id: memory for memory in load_memories()}
    assert memories[3].theme == "API 설계"
    assert memories[2].body.endswith("\n\n****** KNOWLEDGE APPENDED 1 ********\nFK 는 기존을 따른다")
    assert len(memories[2].sources) == 2
    with pytest.raises(MemoryApiError):
        writer.append(99, MemoryAddition("없음", ()))


def test_should_call_server_for_search_create_and_append(fake_api):
    fake_api.answer(
        "POST",
        "/memories/search",
        {"items": [{"memory_id": 5, "kind": "knowledge", "theme": "테이블 설계", "body": "본문", "score": 0.8}]},
    )
    fake_api.answer("POST", "/memories", {"memory_id": 6})
    fake_api.answer("POST", "/memories/6/append", {"memory_id": 6})

    assert DefaultMemoryApiReader().search(QUERY) == (
        MemorySearchHit(5, MemoryKind.KNOWLEDGE, "테이블 설계", "본문", 0.8),
    )
    assert DefaultMemoryApiWriter().create(NEW) == 6
    assert DefaultMemoryApiWriter().append(6, MemoryAddition("더", ())) == 6

    sent = {(method, path): body for method, path, body in fake_api.requests}
    assert sent[("POST", "/memories/search")] == {
        "kind": "knowledge",
        "query": "아무 검색어",
        "persona_ids": [1],
        "theme": None,
        "limit": 10,
    }
    assert sent[("POST", "/memories")]["source"] == [{"quote": "페이지로", "plan_id": 3}]
    assert sent[("POST", "/memories/6/append")] == {"body": "더", "source": []}
