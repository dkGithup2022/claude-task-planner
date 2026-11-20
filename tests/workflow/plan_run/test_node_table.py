"""끝 알림의 노드 수 줄과 표."""

from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.workflow.plan_run.notify.node_table import count_line, node_table

PLAN_ID = 7


def _node(node_id: int, title: str, status: PlanNodeStatus) -> PlanNode:
    return PlanNode(node_id=node_id, title=title, kind=NodeKind.DOCUMENT, persona_ids=(), output_spec="", status=status)


def _plan(*nodes: PlanNode) -> Plan:
    return Plan(PLAN_ID, "문서", "# 명령", (1,), PlanStatus.RUNNING, "2026-11-20T00:00:00Z", nodes, ())


def test_should_count_only_statuses_that_appear():
    plan = _plan(
        _node(1, "가", PlanNodeStatus.DONE), _node(2, "나", PlanNodeStatus.SKIPPED), _node(3, "다", PlanNodeStatus.DONE)
    )
    assert count_line(plan) == "노드 3개: 완료 2, 건너뜀 1"
    assert count_line(_plan()) == "노드 0개"


def test_should_fill_result_or_reason_by_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # 결과 파일 위치는 작업 폴더 기준
    plan = _plan(
        _node(1, "결과", PlanNodeStatus.DONE),
        _node(2, "확인", PlanNodeStatus.DONE),
        _node(3, "건너뜀", PlanNodeStatus.SKIPPED),
        _node(4, "실패", PlanNodeStatus.FAILED),
        _node(5, "할 일", PlanNodeStatus.TODO),
    )
    long_words = "가" * 70 + "\n둘째 줄"
    runs = {
        1: NodeRun(1, PlanNodeStatus.DONE),
        2: NodeRun(1, PlanNodeStatus.DONE, confirm=long_words),
        3: NodeRun(2, PlanNodeStatus.SKIPPED, skipped_reason="사용자가 건너뜀", failed_reason="막힘"),
        4: NodeRun(1, PlanNodeStatus.FAILED, failed_reason="결과 파일 없음"),
        5: None,
    }
    assert node_table(plan, runs).split("\n") == [
        "| 노드 | 제목 | 상태 | 회차 | 결과 / 이유 |",
        "|---|---|---|---|---|",
        f"| 1 | 결과 | 완료 | 1 | .plan/{PLAN_ID}/nodes/1/result.md |",
        f'| 2 | 확인 | 완료 | 1 | 확인: "{"가" * 60}…" |',
        "| 3 | 건너뜀 | 건너뜀 | 2 | 사용자가 건너뜀 (실패 이유: 막힘) |",
        "| 4 | 실패 | 실패 | 1 | 실패 이유: 결과 파일 없음 |",
        "| 5 | 할 일 | 할 일 | - |  |",
    ]


def test_should_put_multiline_failure_reason_in_one_cell(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plan = _plan(_node(1, "가", PlanNodeStatus.SKIPPED))
    reason = "claude 실패 (exit 1): Error: auth\n  at a | b\n"
    runs = {1: NodeRun(1, PlanNodeStatus.SKIPPED, skipped_reason="사용자가 건너뜀", failed_reason=reason)}
    assert node_table(plan, runs).split("\n")[2] == (
        "| 1 | 가 | 건너뜀 | 1 | 사용자가 건너뜀 (실패 이유: claude 실패 (exit 1): Error: auth at a \\| b) |"
    )
