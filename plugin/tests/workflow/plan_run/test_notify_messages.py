"""끝 알림의 경우별 글. 막힘과 차례를 다 씀은 CLI 시험으로 만들기 어려워 여기서 본다."""

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.workflow.plan_run.notify.notify_messages import (
    blocked_message,
    remaining_message,
    stopped_message,
)
from task_planner.workflow.plan_run.stopped_node import BROKEN, IN_ROUNDS, NO_PROMPT, StopPoint


def _plan() -> Plan:
    nodes = (
        PlanNode(1, "가", NodeKind.DOCUMENT, (), "", PlanNodeStatus.DONE),
        PlanNode(2, "나", NodeKind.DOCUMENT, (), "", PlanNodeStatus.TODO),
    )
    return Plan(7, "문서", "# 명령", (1,), PlanStatus.RUNNING, "2026-11-20T00:00:00Z", nodes, ())


def test_should_show_where_it_stopped():
    assert stopped_message(StopPoint(IN_ROUNDS, (3,), "노드 3 에서 멈춤 글"), 7) == "노드 3 에서 멈춤 글"
    assert stopped_message(StopPoint(BROKEN, (4, 5)), 7) == (
        "노드 4, 5 에서 멈췄습니다. 이어 하려면 /task-planner:plan-run 7"
    )
    assert stopped_message(StopPoint(NO_PROMPT, (4,)), 7) == (
        "노드 4 의 작업 지시를 만들지 못해 멈췄습니다. 이어 하려면 /task-planner:plan-run 7"
    )


def test_should_show_table_when_blocked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    text = blocked_message(_plan(), {1: None, 2: None})
    assert text.split("\n")[0] == (
        '계획 7 "문서" 에서 더 실행할 수 있는 노드가 없습니다. 노드 2개: 완료 1, 할 일 1. '
        "이어 하려면 /task-planner:plan-run 7"
    )
    assert "| 2 | 나 | 할 일 | - |  |" in text


def test_should_tell_remaining_nodes():
    assert remaining_message(_plan()) == ('계획 7 "문서" 에 남은 노드가 있습니다. 이어 하려면 /task-planner:plan-run 7')
