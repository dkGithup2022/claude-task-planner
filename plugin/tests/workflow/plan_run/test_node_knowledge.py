"""작업 지시 만들기의 지식 찾기: 검색어, 확인 노드, 두 종류, 검색 실패를 본다 (가짜 지식 검색)."""

from task_planner.model.memory.memory_kind import MemoryKind
from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_planner.port.memory_api.memory_api_error import MemoryApiError
from task_planner.workflow.plan_run.prompts.write_prompts import node_knowledge as knowledge_module
from task_planner.workflow.plan_run.prompts.write_prompts.node_knowledge import node_knowledge
from task_planner.workflow.plan_run.prompts.write_prompts.search_word import build_search_word

SPEC = "### 하는 일\n엔드포인트를 정한다\n\n### 산출물\n- 형태: 문서\nAPI 목록\n\n### 그 외 설명\n(없음)"


def _node(kind: NodeKind = NodeKind.DOCUMENT, persona_ids: tuple[int, ...] = (2,)) -> PlanNode:
    return PlanNode(7, "API 설계", kind, persona_ids, SPEC, PlanNodeStatus.TODO)


class FakeReader:
    """종류마다 정해 둔 결과를 돌려주고, 받은 검색 요청을 모은다."""

    def __init__(self, hits_by_kind: dict[MemoryKind, list[MemorySearchHit]], fails: bool = False) -> None:
        self.hits_by_kind = hits_by_kind
        self.fails = fails
        self.queries: list = []

    def search(self, query):
        self.queries.append(query)
        if self.fails:
            raise MemoryApiError("POST /memories/search 에 연결하지 못함")
        return tuple(self.hits_by_kind.get(query.kind, []))


def _use_reader(monkeypatch, reader: FakeReader) -> None:
    monkeypatch.setattr(knowledge_module, "memory_api_reader", lambda: reader)


def test_should_search_with_title_and_spec_without_heading_lines():
    assert build_search_word(_node()) == "API 설계\n엔드포인트를 정한다\n\n- 형태: 문서\nAPI 목록\n\n(없음)"


def test_should_find_knowledge_and_attitude_of_owner(monkeypatch):
    knowledge = [MemorySearchHit(1, MemoryKind.KNOWLEDGE, "API 서버 개발", "엔드포인트마다 에러 코드\n", 0.5)]
    attitude = [MemorySearchHit(4, MemoryKind.ATTITUDE, "문서 작성", "결론부터 쓴다", 0.3)]
    reader = FakeReader({MemoryKind.KNOWLEDGE: knowledge * 7, MemoryKind.ATTITUDE: attitude})
    _use_reader(monkeypatch, reader)

    text, warning = node_knowledge(_node())

    assert [(query.kind, query.persona_ids) for query in reader.queries] == [
        (MemoryKind.KNOWLEDGE, (2,)),
        (MemoryKind.ATTITUDE, (2,)),
    ]
    assert text.count("## API 서버 개발 (작업 지식, 지식 1)\n엔드포인트마다 에러 코드") == 5  # 종류마다 앞 5 개
    assert text.endswith("## 문서 작성 (태도, 지식 4)\n결론부터 쓴다")
    assert warning is None


def test_should_not_search_for_confirm_node(monkeypatch):
    reader = FakeReader({})
    _use_reader(monkeypatch, reader)

    assert node_knowledge(_node(NodeKind.HITL, ())) == ("(없음)", None)
    assert reader.queries == []


def test_should_say_none_when_nothing_found(monkeypatch):
    _use_reader(monkeypatch, FakeReader({}))
    assert node_knowledge(_node()) == ("(없음)", None)


def test_should_say_search_failed_with_warning(monkeypatch):
    _use_reader(monkeypatch, FakeReader({}, fails=True))

    text, warning = node_knowledge(_node())

    assert text == "(검색 실패)"
    assert warning == "지식 검색 실패 (POST /memories/search 에 연결하지 못함)"
