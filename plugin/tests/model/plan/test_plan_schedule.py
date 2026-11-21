"""다음 노드 계산. 시뮬레이션의 계획 7: 1 → 2, 1 → 3, 2 → 4, 3 → 4, 4 → 5 (4 는 확인 노드)."""

import pytest

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_schedule import (
    nodes_to_skip,
    plan_progress,
    runnable_nodes,
    waiting_confirm_nodes,
)
from task_planner.model.plan.plan_status import PlanStatus

TODO, RUNNING, DONE, FAILED, SKIPPED = (
    PlanNodeStatus.TODO,
    PlanNodeStatus.RUNNING,
    PlanNodeStatus.DONE,
    PlanNodeStatus.FAILED,
    PlanNodeStatus.SKIPPED,
)
EDGES = ((1, 2), (1, 3), (2, 4), (3, 4), (4, 5))


def _plan(statuses: dict[int, PlanNodeStatus], edges=EDGES, confirm_ids=(4,)) -> Plan:
    nodes = tuple(
        PlanNode(
            node_id,
            f"노드 {node_id}",
            NodeKind.HITL if node_id in confirm_ids else NodeKind.CODE,
            () if node_id in confirm_ids else (1,),
            "### 하는 일",
            status,
        )
        for node_id, status in statuses.items()
    )
    plan_edges = tuple(PlanEdge(order, from_id, to_id) for order, (from_id, to_id) in enumerate(edges, start=1))
    return Plan(7, "계획", "# 명령", (1,), PlanStatus.RUNNING, "2026-11-20T00:00:00Z", nodes, plan_edges)


def _all(status: PlanNodeStatus, **changed: PlanNodeStatus) -> dict[int, PlanNodeStatus]:
    statuses = dict.fromkeys(range(1, 6), status)
    statuses.update({int(key[1:]): value for key, value in changed.items()})
    return statuses


def _ids(nodes) -> list[int]:
    return [node.node_id for node in nodes]


@pytest.mark.parametrize(
    ("statuses", "limit", "runnable", "confirm"),
    [
        (_all(TODO), 3, [1], []),
        (_all(TODO, n1=DONE), 3, [2, 3], []),
        (_all(TODO, n1=DONE, n2=RUNNING), 2, [3], []),
        (_all(TODO, n1=DONE), 1, [2], []),
        (_all(TODO, n1=DONE, n2=DONE, n3=FAILED), 3, [], []),
        (_all(TODO, n1=DONE, n2=DONE, n3=DONE), 3, [], [4]),
        (_all(TODO, n1=DONE, n2=DONE, n3=SKIPPED), 3, [], [4]),
        (_all(DONE, n5=TODO), 3, [5], []),
        (_all(DONE), 3, [], []),
    ],
)
def test_should_pick_nodes_whose_prerequisites_are_finished(statuses, limit, runnable, confirm):
    plan = _plan(statuses)
    assert _ids(runnable_nodes(plan, limit)) == runnable
    assert _ids(waiting_confirm_nodes(plan)) == confirm


def test_should_pick_nothing_when_limit_is_zero_or_less():
    assert runnable_nodes(_plan(_all(TODO)), 0) == ()
    assert runnable_nodes(_plan(_all(TODO)), -1) == ()


@pytest.mark.parametrize(
    ("statuses", "node_id", "skipped"),
    [
        (_all(TODO, n1=DONE, n2=DONE), 3, (3,)),  # 4 는 2(완료)에도 기댄다
        (_all(TODO), 1, (1, 2, 3, 4, 5)),
        (_all(TODO, n1=DONE, n2=SKIPPED), 3, (3, 4, 5)),
        (_all(TODO, n1=DONE, n2=DONE, n4=DONE), 3, (3,)),  # 완료된 노드는 넣지 않는다
        (_all(TODO, n1=DONE, n2=RUNNING), 3, (3,)),  # 4 의 앞 노드 2 가 아직 돈다
    ],
)
def test_should_spread_skip_only_to_nodes_depending_on_skipped_nodes(statuses, node_id, skipped):
    assert nodes_to_skip(_plan(statuses), node_id) == skipped


def test_should_not_skip_running_follower():
    plan = _plan({1: TODO, 2: RUNNING}, edges=((1, 2),), confirm_ids=())
    assert nodes_to_skip(plan, 1) == (1,)


def test_should_report_progress():
    progress = plan_progress(_plan(_all(DONE, n3=SKIPPED)))
    assert progress.finished and not progress.blocked
    assert progress.counts[DONE] == 4 and progress.counts[SKIPPED] == 1 and progress.counts[TODO] == 0

    moving = plan_progress(_plan(_all(TODO, n1=DONE, n2=DONE, n3=FAILED)))
    assert not moving.finished and not moving.blocked  # 실패가 있으면 실패 처리로 먼저 묻는다


def test_should_report_blocked_when_nothing_can_move():
    # 2 와 3 이 서로를 기다린다 (확정 전 간선 점검이 막는 순환이지만, 계산은 막힘으로 알려야 한다)
    plan = _plan({1: DONE, 2: TODO, 3: TODO}, edges=((1, 2), (2, 3), (3, 2)), confirm_ids=())
    progress = plan_progress(plan)
    assert not progress.finished and progress.blocked
