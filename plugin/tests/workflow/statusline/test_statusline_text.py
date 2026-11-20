from datetime import UTC, datetime

import pytest

from task_plan_manager.model.progress.closed_progress import ClosedProgress
from task_plan_manager.model.progress.feedback_progress import FeedbackProgress
from task_plan_manager.model.progress.planning_progress import PlanningProgress
from task_plan_manager.model.progress.progress_event import ProgressDetail, ProgressEvent
from task_plan_manager.model.progress.reinforce_phase import ReinforcePhase
from task_plan_manager.model.progress.reinforce_progress import ReinforceProgress
from task_plan_manager.model.progress.run_node import RunNode
from task_plan_manager.model.progress.run_phase import RunPhase
from task_plan_manager.model.progress.run_progress import RunProgress
from task_plan_manager.workflow.statusline.statusline_text import elapsed_text, statusline_text

NOW = datetime(2026, 11, 20, 5, 10, 0, tzinfo=UTC)


def lines_of(detail: ProgressDetail) -> list[str]:
    return statusline_text(ProgressEvent(at="2026-11-20T05:00:00Z", session_id="s1", plan_id=11, detail=detail), NOW)


def test_should_show_planning():
    assert lines_of(PlanningProgress(started_at="2026-11-20T05:09:25Z")) == [
        "계획 11 │ 계획 입력 ✓ › [계획 세우기] › 계획 피드백 › 지식 강화 › 실행",
        "계획 세우기 - 적합한 크기의 계획 세우는 중... (35초째)",
    ]


def test_should_show_feedback_with_commands():
    assert lines_of(FeedbackProgress(editing_since=None)) == [
        "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › [계획 피드백] › 지식 강화 › 실행",
        "고칠 곳이 있으면 대화로 말하세요. 다 됐으면 아래 명령을 실행하세요",
        "확정: /task_plan_manager:plan-go 11   ·   취소: /task_plan_manager:plan-cancel 11",
    ]


def test_should_show_editing_in_place_of_the_guide():
    assert lines_of(FeedbackProgress(editing_since="2026-11-20T05:09:54Z"))[1] == "계획을 고치는 중입니다 (6초째)"


def test_should_show_knowledge_draft():
    detail = ReinforceProgress(ReinforcePhase.DRAFT, 3, 7, "하위 기획 작성", "2026-11-20T05:09:48Z")
    assert lines_of(detail) == [
        "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › 계획 피드백 ✓ › [지식 강화] › 실행",
        "지식 후보 - 3번째 / 7개 중 : 하위 기획 작성",
        "본문 초안을 쓰는 중입니다 (12초째)",
        "그만두기: /task_plan_manager:plan-cancel 11",
    ]


def test_should_show_ready_to_run():
    assert lines_of(RunProgress(RunPhase.READY, 0, 10)) == [
        "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › 계획 피드백 ✓ › 지식 강화 ✓ › [실행]",
        "승인했습니다. 실행하려면 아래 명령을 실행하세요",
        "실행: /task_plan_manager:plan-run 11",
    ]


def test_should_show_running_node():
    detail = RunProgress(RunPhase.NODES, 5, 10, (RunNode(50, "API 문서 작성", "2026-11-20T05:07:00Z"),))
    assert lines_of(detail) == [
        "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › 계획 피드백 ✓ › 지식 강화 ✓ › [실행]",
        "노드 실행 - 6번째 / 10개 중 : 50 API 문서 작성",
        "노드를 실행하는 중입니다. 기다리세요 (3분째)",
    ]


def test_should_name_earliest_node_and_count_the_others():
    nodes = (RunNode(52, "백엔드", "2026-11-20T05:09:00Z"), RunNode(51, "UI 문서 작성", "2026-11-20T05:06:00Z"))
    assert lines_of(RunProgress(RunPhase.NODES, 6, 10, nodes))[1:] == [
        "노드 실행 - 7번째 / 10개 중 : 51 UI 문서 작성 외 1개",
        "노드를 실행하는 중입니다. 기다리세요 (4분째)",
    ]


def test_should_show_finished_with_every_stage_done():
    assert lines_of(RunProgress(RunPhase.FINISHED, 10, 10)) == [
        "계획 11 │ 계획 입력 ✓ › 계획 세우기 ✓ › 계획 피드백 ✓ › 지식 강화 ✓ › 실행 ✓",
        "계획을 마쳤습니다",
    ]


@pytest.mark.parametrize(
    "detail",
    [
        ReinforceProgress(ReinforcePhase.EXTRACT, None, None, None, "2026-11-20T05:09:00Z"),
        ReinforceProgress(ReinforcePhase.CHOOSE, 3, 7, "하위 기획 작성", None),
        ReinforceProgress(ReinforcePhase.REVIEW, 3, 7, "하위 기획 작성", None),
        ReinforceProgress(ReinforcePhase.FINALIZE, 3, 7, "하위 기획 작성", "2026-11-20T05:09:00Z"),
        RunProgress(RunPhase.PROMPTS, 4, 10),
        RunProgress(RunPhase.CONFIRM, 6, 10, (RunNode(52, "결과 검토", None),)),
        RunProgress(RunPhase.FAILED, 6, 10, (RunNode(53, "배포 스크립트", None),)),
    ],
)
def test_should_show_only_the_stage_line_where_no_text_was_decided(detail):
    assert len(lines_of(detail)) == 1


def test_should_show_nothing_after_rejection():
    assert lines_of(ClosedProgress()) == []


@pytest.mark.parametrize(
    ("started_at", "expected"),
    [("2026-11-20T05:09:01Z", "59초째"), ("2026-11-20T05:09:00Z", "1분째"), ("2026-11-20T05:10:30Z", "0초째")],
)
def test_should_count_seconds_then_minutes(started_at, expected):
    assert elapsed_text(started_at, NOW) == expected
