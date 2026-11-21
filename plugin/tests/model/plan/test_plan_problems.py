"""Plan.problems: 확정·실행 전에 고쳐야 할 문제."""

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus


def _plan(edges: tuple[PlanEdge, ...], nodes: tuple[PlanNode, ...] | None = None) -> Plan:
    default_nodes = tuple(
        PlanNode(node_id, f"노드{node_id}", NodeKind.DOCUMENT, (1,), "### 하는 일", PlanNodeStatus.TODO)
        for node_id in (1, 2, 3)
    )
    return Plan(7, "계획", "# 명령", (1,), PlanStatus.REVIEWING, "2026-11-19T00:00:00Z", nodes or default_nodes, edges)


def test_should_have_no_problem_for_a_clean_plan():
    assert _plan((PlanEdge(1, 1, 2), PlanEdge(2, 2, 3), PlanEdge(3, 1, 3))).problems() == ()


def test_should_report_each_cycle_once():
    problems = _plan((PlanEdge(1, 1, 2), PlanEdge(2, 2, 3), PlanEdge(3, 3, 1))).problems()
    assert problems == ("순환: 1 노드1 → 2 노드2 → 3 노드3 → 1 노드1",)


def test_should_report_edge_end_problems():
    edges = (PlanEdge(5, 9, 1), PlanEdge(6, 2, 2), PlanEdge(3, 1, 3), PlanEdge(7, 1, 3))
    assert _plan(edges).problems() == (
        "간선 5: 앞 노드 9 가 계획에 없습니다",
        "간선 6: 노드 2 이 자기 자신을 잇습니다",
        "간선 3, 7: 같은 노드를 잇습니다 (1 → 3)",
    )


def test_should_report_node_without_persona_except_hitl():
    nodes = (
        PlanNode(1, "조사", NodeKind.RESEARCH, (), "### 하는 일", PlanNodeStatus.TODO),
        PlanNode(2, "확인", NodeKind.HITL, (), "### 하는 일", PlanNodeStatus.TODO),
    )
    assert _plan((), nodes).problems() == ("노드 1 조사: 담당 페르소나가 없습니다",)
