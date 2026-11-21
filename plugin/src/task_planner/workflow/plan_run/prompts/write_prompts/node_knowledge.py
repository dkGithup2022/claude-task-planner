"""작업 지시 생성기에 넣을 지식: 노드의 담당 페르소나로 작업 지식과 태도를 한 번씩 찾아 종류마다 앞 5 개.

생성기 프롬프트가 관계있는 것만 스스로 고르므로 따로 거르지 않는다 (사용자, 2026-11-21).
본문은 덧붙임까지 자르지 않는다. 검색이 실패하면 "(검색 실패)" 를 넣고 경고를 남긴다. 작업 지시 만들기는 멈추지 않는다.
"""

from __future__ import annotations

from task_planner.model.memory.memory_kind import MemoryKind
from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_node import PlanNode
from task_planner.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_planner.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_planner.port.memory_api.memory_api_choice import memory_api_reader
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.workflow.plan_run.prompts.write_prompts.search_word import build_search_word

KNOWLEDGE_COUNT = 5  # 종류마다 넣을 지식 수
SEARCHED_KINDS = (MemoryKind.KNOWLEDGE, MemoryKind.ATTITUDE)
KIND_LABEL = {MemoryKind.KNOWLEDGE: "작업 지식", MemoryKind.ATTITUDE: "태도"}
NO_KNOWLEDGE = "(없음)"
SEARCH_FAILED = "(검색 실패)"


def node_knowledge(node: PlanNode) -> tuple[str, str | None]:
    """(생성기 입력의 "담당 페르소나로 검색한 태도와 지식" 절에 넣을 글, 경고). 경고가 없으면 None.
    확인 노드이거나 담당 페르소나가 없으면 찾지 않는다."""
    if node.kind is NodeKind.HITL or not node.persona_ids:
        return NO_KNOWLEDGE, None
    try:
        hits = [hit for kind in SEARCHED_KINDS for hit in search_node_knowledge(node, kind)]
    except MemoryApiError as error:
        return SEARCH_FAILED, f"지식 검색 실패 ({error})"
    return found_knowledge_md(hits), None


def search_node_knowledge(node: PlanNode, kind: MemoryKind) -> tuple[MemorySearchHit, ...]:
    """담당 페르소나가 쌓은 이 종류의 지식 가운데 노드와 가까운 것 앞 5 개."""
    query = MemorySearchQuery(kind=kind, query=build_search_word(node), persona_ids=node.persona_ids)
    return memory_api_reader().search(query)[:KNOWLEDGE_COUNT]


def found_knowledge_md(hits: list[MemorySearchHit]) -> str:
    """지식마다 "## <작업 이름> (<종류>, 지식 <id>)" 줄 아래에 본문 전체. 없으면 "(없음)"."""
    if not hits:
        return NO_KNOWLEDGE
    return "\n\n".join(
        f"## {hit.theme} ({KIND_LABEL.get(hit.kind, hit.kind.value)}, 지식 {hit.memory_id})\n{hit.body.strip()}"
        for hit in hits
    )
