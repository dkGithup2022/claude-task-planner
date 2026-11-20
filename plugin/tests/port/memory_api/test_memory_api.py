from dataclasses import replace

import pytest

from task_plan_manager.model.memory.memory_kind import MemoryKind
from task_plan_manager.model.memory.memory_source import MemorySource
from task_plan_manager.port.memory_api.default_memory_api_reader import DefaultMemoryApiReader
from task_plan_manager.port.memory_api.default_memory_api_writer import DefaultMemoryApiWriter
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


def test_should_create_get_and_update_in_mock():
    writer, reader = MockMemoryApiWriter(), MockMemoryApiReader()
    assert writer.create(NEW) == 3
    appended = reader.get(2).append("FK 는 기존을 따른다", (MemorySource("fk", 1),))
    assert writer.update(appended) == 2

    memories = {memory.memory_id: memory for memory in load_memories()}
    assert memories[3].theme == "API 설계"
    assert memories[2].body.endswith("\n\n****** KNOWLEDGE APPENDED 1 ********\nFK 는 기존을 따른다")
    assert len(memories[2].sources) == 2
    with pytest.raises(MemoryApiError):
        reader.get(99)
    with pytest.raises(MemoryApiError):
        writer.update(replace(appended, memory_id=99))


def test_should_call_server_for_search_create_get_and_update(fake_api):
    fake_api.answer(
        "POST",
        "/memories/search",
        {"items": [{"memory_id": 5, "kind": "knowledge", "theme": "테이블 설계", "body": "본문", "score": 0.8}]},
    )
    fake_api.answer("POST", "/memories", {"memory_id": 6})
    stored = {"memory_id": 6, "kind": "knowledge", "theme": "테이블 설계", "body": "본문", "persona_ids": [1],
              "source": [{"quote": "fk", "plan_id": 1}]}  # fmt: skip
    fake_api.answer("GET", "/memories/6", stored)
    fake_api.answer("PATCH", "/memories/6", {"memory_id": 6})

    assert DefaultMemoryApiReader().search(QUERY) == (
        MemorySearchHit(5, MemoryKind.KNOWLEDGE, "테이블 설계", "본문", 0.8),
    )
    assert DefaultMemoryApiWriter().create(NEW) == 6
    memory = DefaultMemoryApiReader().get(6)
    assert memory.theme == "테이블 설계" and memory.sources == (MemorySource("fk", 1),)
    assert DefaultMemoryApiWriter().update(memory.append("더", (MemorySource("더 말", 2),))) == 6

    sent = {(method, path): body for method, path, body in fake_api.requests}
    assert sent[("POST", "/memories/search")] == {
        "kind": "knowledge",
        "query": "아무 검색어",
        "persona_ids": [1],
        "theme": None,
        "limit": 10,
    }
    assert sent[("POST", "/memories")]["source"] == [{"quote": "페이지로", "plan_id": 3}]
    assert sent[("PATCH", "/memories/6")] == {
        "body": "본문\n\n****** KNOWLEDGE APPENDED 1 ********\n더",
        "source": [{"quote": "fk", "plan_id": 1}, {"quote": "더 말", "plan_id": 2}],
    }
