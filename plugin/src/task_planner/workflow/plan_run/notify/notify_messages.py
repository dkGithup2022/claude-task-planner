"""끝 알림의 글. 경우마다 함수 하나. 읽기·쓰기 없이 받은 값으로만 만든다."""

from __future__ import annotations

from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.plan.plan import Plan
from task_planner.workflow.plan_run.notify.node_table import count_line, node_table
from task_planner.workflow.plan_run.stopped_node import BROKEN, IN_ROUNDS, StopPoint


def stopped_message(stopped: StopPoint, plan_id: int) -> str:
    """이번 실행에서 멈췄을 때. 노드 실행 중 멈춤은 멈춤 표시에 남긴 글을 그대로 쓴다."""
    if stopped.reason == IN_ROUNDS:
        return stopped.message
    node_ids = joined_ids(stopped.node_ids)
    if stopped.reason == BROKEN:
        return f"노드 {node_ids} 에서 멈췄습니다. {resume_hint(plan_id)}"
    return f"노드 {node_ids} 의 작업 지시를 만들지 못해 멈췄습니다. {resume_hint(plan_id)}"


def finished_message(plan: Plan, node_runs: dict[int, NodeRun | None]) -> str:
    """모든 노드가 끝났을 때. 예: 계획 13 "…" 을 마쳤습니다. 노드 5개: 완료 4, 건너뜀 1 + 표"""
    return f"{plan_name(plan)} 을 마쳤습니다. {count_line(plan)}\n\n{node_table(plan, node_runs)}"


def blocked_message(plan: Plan, node_runs: dict[int, NodeRun | None]) -> str:
    """끝나지 않았는데 더 실행할 노드가 없을 때."""
    head = f"{plan_name(plan)} 에서 더 실행할 수 있는 노드가 없습니다. {count_line(plan)}."
    return f"{head} {resume_hint(plan.plan_id)}\n\n{node_table(plan, node_runs)}"


def remaining_message(plan: Plan) -> str:
    """정해 둔 차례를 다 썼는데 남은 노드가 있을 때."""
    return f"{plan_name(plan)} 에 남은 노드가 있습니다. {resume_hint(plan.plan_id)}"


def plan_name(plan: Plan) -> str:
    return f'계획 {plan.plan_id} "{plan.title}"'


def resume_hint(plan_id: int) -> str:
    return f"이어 하려면 /task-planner:plan-run {plan_id}"


def joined_ids(node_ids: tuple[int, ...]) -> str:
    return ", ".join(str(node_id) for node_id in node_ids)
