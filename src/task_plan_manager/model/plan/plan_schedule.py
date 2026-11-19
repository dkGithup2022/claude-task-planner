"""계획 노드의 실행 순서 계산. 노드 상태(PlanNode.status)와 간선만 본다. 순수 함수.
기존 persona-enhancer-pg2/plugin/client/plan/schedule.py:21-75, run.py:263-281 에서 루프를 뺐다.
끝난 노드 = 완료(done) 또는 건너뜀(skipped). 같은 차례에 고를 노드가 여럿이면 node_id 작은 순."""

from __future__ import annotations

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_progress import PlanProgress

FINISHED = frozenset({PlanNodeStatus.DONE, PlanNodeStatus.SKIPPED})


def runnable_nodes(plan: Plan, limit: int) -> tuple[PlanNode, ...]:
    """지금 실행할 일반 노드. todo 이고 확인 노드가 아니고 선행 노드가 모두 끝난 노드를 node_id 순으로 limit 개.
    실패한 노드의 뒤 노드는 선행 노드가 끝나지 않았으므로 저절로 빠진다.
    limit 은 부르는 쪽이 "동시에 돌릴 수 - 지금 도는 수" 로 준다 (빈 자리 채우기, 사용자 2026-11-20)."""
    ready = [node for node in _sorted(plan) if node.kind is not NodeKind.HITL and _ready(plan, node)]
    return tuple(ready[: max(0, limit)])


def waiting_confirm_nodes(plan: Plan) -> tuple[PlanNode, ...]:
    """사용자 확인을 기다리는 확인 노드. todo 이고 선행 노드가 모두 끝난 노드를 node_id 순으로."""
    return tuple(node for node in _sorted(plan) if node.kind is NodeKind.HITL and _ready(plan, node))


def nodes_to_skip(plan: Plan, node_id: int) -> tuple[int, ...]:
    """이 노드를 건너뛸 때 함께 건너뛸 노드 (이 노드 포함).
    뒤 노드는 들어오는 간선이 모두 건너뛴(또는 이번에 건너뛸) 노드에서 올 때만 번진다.
    완료·실행 중인 노드는 넣지 않는다."""
    skipping = [node_id]
    waiting = [node_id]
    while waiting:
        current = waiting.pop(0)
        for follower in _followers(plan, current):
            if follower in skipping or plan.node(follower).status in (PlanNodeStatus.DONE, PlanNodeStatus.RUNNING):
                continue
            if all(
                pre in skipping or plan.node(pre).status is PlanNodeStatus.SKIPPED
                for pre in plan.prerequisites(follower)
            ):
                skipping.append(follower)
                waiting.append(follower)
    return tuple(skipping)


def plan_progress(plan: Plan) -> PlanProgress:
    """상태별 개수와, 끝났는지·막혔는지. 실패한 노드가 있으면 막힘이 아니다 (실패 처리로 먼저 묻는다)."""
    counts = {status: sum(1 for node in plan.nodes if node.status is status) for status in PlanNodeStatus}
    finished = all(node.status in FINISHED for node in plan.nodes)
    moving = bool(
        runnable_nodes(plan, len(plan.nodes))
        or waiting_confirm_nodes(plan)
        or counts[PlanNodeStatus.RUNNING]
        or counts[PlanNodeStatus.FAILED]
    )
    return PlanProgress(counts=counts, finished=finished, blocked=not finished and not moving)


def _ready(plan: Plan, node: PlanNode) -> bool:
    """todo 이고 선행 노드가 모두 끝남."""
    return node.status is PlanNodeStatus.TODO and all(
        plan.node(pre).status in FINISHED for pre in plan.prerequisites(node.node_id)
    )


def _followers(plan: Plan, node_id: int) -> list[int]:
    """간선으로 이 노드에 바로 이어진 뒤 노드."""
    return [edge.to_node_id for edge in plan.edges if edge.from_node_id == node_id]


def _sorted(plan: Plan) -> list[PlanNode]:
    return sorted(plan.nodes, key=lambda node: node.node_id)
