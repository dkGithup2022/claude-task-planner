from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_edge import PlanEdge
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_status import PlanStatus


def _node(node_id: int) -> PlanNode:
    return PlanNode(node_id, f"노드 {node_id}", NodeKind.RESEARCH, (1,), "### 하는 일", PlanNodeStatus.TODO)


def _plan() -> Plan:
    # 11 → 12 → 14, 11 → 13 → 14
    edges = (PlanEdge(1, 11, 12), PlanEdge(2, 11, 13), PlanEdge(3, 12, 14), PlanEdge(4, 13, 14))
    return Plan(
        1,
        "계획",
        "# 명령",
        (1,),
        PlanStatus.REVIEWING,
        "2026-11-19T00:00:00Z",
        tuple(_node(node_id) for node_id in (11, 12, 13, 14)),
        edges,
    )


def test_should_return_only_directly_connected_prerequisites():
    plan = _plan()
    assert plan.prerequisites(14) == (12, 13)
    assert plan.prerequisites(11) == ()


def test_should_find_node_or_raise_key_error():
    plan = _plan()
    assert plan.node(13).title == "노드 13"
    try:
        plan.node(99)
        raise AssertionError("KeyError 가 나야 한다")
    except KeyError:
        pass


def test_should_allow_only_draft_status_transitions():
    assert PlanStatus.REVIEWING.can_move_to(PlanStatus.APPROVED)
    assert PlanStatus.REVIEWING.can_move_to(PlanStatus.REJECTED)
    assert not PlanStatus.DRAFTING.can_move_to(PlanStatus.APPROVED)
    assert not PlanStatus.REJECTED.can_move_to(PlanStatus.RUNNING)
    assert not PlanStatus.DONE.can_move_to(PlanStatus.RUNNING)
