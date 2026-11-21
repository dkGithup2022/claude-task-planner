"""pick_relevant_contexts: 가짜 claude 로 입력 글 모양과 고른 id 정리를 본다."""

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.claude_utils.search_utils.context_item import ContextItem
from task_plan_manager.claude_utils.search_utils.pick_relevant_contexts import (
    RELEVANT_CONTEXT,
    pick_relevant_contexts,
)
from task_plan_manager.claude_utils.search_utils.prompt_relevant_context_output import RelevantContextOutput

ITEMS = [
    ContextItem(5, "문서 작성 계획", "검토를 마지막 노드로 따로 두지 않는다\n"),
    ContextItem(7, "서비스 설계 문서 작성", "도메인 문서 다음에 API 문서"),
    ContextItem(3, "API 서버 개발", "엔드포인트마다 에러 코드"),
]


def _fake_caller(ids: list[int], seen: list[tuple[object, str]]):
    def caller(spec, user_input):
        seen.append((spec, user_input))
        return RelevantContextOutput(ids=ids), PromptCallRecord({"user": user_input}, {"ok": True})

    return caller


def test_should_send_task_and_contexts_to_haiku():
    seen: list[tuple[object, str]] = []
    pick_relevant_contexts("- 이름: API 설계", ITEMS[:2], _fake_caller([], seen))

    spec, user_input = seen[0]
    assert spec is RELEVANT_CONTEXT and RELEVANT_CONTEXT.model == "haiku"
    assert user_input == (
        "# 실제 작업\n- 이름: API 설계\n\n# 컨텍스트\n"
        "## id 5: 문서 작성 계획\n검토를 마지막 노드로 따로 두지 않는다\n\n"
        "## id 7: 서비스 설계 문서 작성\n도메인 문서 다음에 API 문서\n"
    )


def test_should_keep_order_and_drop_unknown_and_repeated_ids():
    ids, record = pick_relevant_contexts("작업", ITEMS, _fake_caller([7, 99, 5, 7], []))
    assert ids == (7, 5)
    assert record.response == {"ok": True}


def test_should_keep_at_most_five_ids():
    many = [ContextItem(number, f"작업 {number}", "본문") for number in range(1, 9)]
    ids, _ = pick_relevant_contexts("작업", many, _fake_caller([8, 7, 6, 5, 4, 3, 2], []))
    assert ids == (8, 7, 6, 5, 4)


def test_should_return_nothing_when_haiku_picks_nothing():
    ids, _ = pick_relevant_contexts("작업", ITEMS, _fake_caller([], []))
    assert ids == ()
