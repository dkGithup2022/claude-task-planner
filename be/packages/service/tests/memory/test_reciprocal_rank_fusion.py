"""검색 결과를 순위로 합치는 RRF 시험."""

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_search_hit import MemorySearchHit
from task_plan_server.service.memory.search_rank.reciprocal_rank_fusion import (
    RANK_CONSTANT,
    reciprocal_rank_fusion,
)


def _hit(memory_id: int, score: float = 0.5) -> MemorySearchHit:
    return MemorySearchHit(memory_id, MemoryKind.PLAN, f"작업 {memory_id}", "본문", score)


def test_should_put_memory_found_by_both_first_when_merged() -> None:
    # given: 2 는 두 목록 모두 2 위, 1 과 3 은 한 목록에서만 1 위
    text_hits = [_hit(1), _hit(2)]
    vector_hits = [_hit(3), _hit(2)]

    # when
    merged = reciprocal_rank_fusion(text_hits, vector_hits)

    # then
    assert [hit.memory_id for hit in merged] == [2, 1, 3]
    assert merged[0].score == 2 / (RANK_CONSTANT + 2)
    assert merged[1].score == 1 / (RANK_CONSTANT + 1)


def test_should_keep_order_of_single_list_when_other_is_empty() -> None:
    merged = reciprocal_rank_fusion([_hit(5, 0.9), _hit(4, 0.1)], [])

    assert [hit.memory_id for hit in merged] == [5, 4]
    assert [hit.score for hit in merged] == [1 / (RANK_CONSTANT + 1), 1 / (RANK_CONSTANT + 2)]


def test_should_return_empty_when_all_lists_are_empty() -> None:
    assert reciprocal_rank_fusion([], []) == []
