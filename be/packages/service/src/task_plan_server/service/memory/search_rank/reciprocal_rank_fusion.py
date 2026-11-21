from dataclasses import replace

from task_plan_server.model.memory.memory_search_hit import MemorySearchHit

# RRF 의 관례값. 클수록 순위가 낮은 결과의 몫이 높은 결과와 비슷해진다
RANK_CONSTANT = 60


def reciprocal_rank_fusion(*rankings: list[MemorySearchHit]) -> list[MemorySearchHit]:
    """여러 검색 결과를 순위로 합친다 (Reciprocal Rank Fusion).

    지식마다 나온 목록의 1 / (RANK_CONSTANT + 순위) 를 더한 값을 점수로 두고 점수 높은 순으로.
    점수가 같으면 먼저 넘긴 목록에서 먼저 나온 지식이 앞이다. 본문 등은 처음 나온 결과의 것을 쓴다.
    """
    scores: dict[int, float] = {}
    first_hits: dict[int, MemorySearchHit] = {}
    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            scores[hit.memory_id] = scores.get(hit.memory_id, 0.0) + 1 / (RANK_CONSTANT + rank)
            first_hits.setdefault(hit.memory_id, hit)
    ordered_ids = sorted(scores, key=lambda memory_id: scores[memory_id], reverse=True)
    return [replace(first_hits[memory_id], score=scores[memory_id]) for memory_id in ordered_ids]
