"""prepare_show 가 사용자에게 보일 글: 계획 한 줄, 노드 표, 확인 노드, 경고."""

from __future__ import annotations

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode


def build_summary(plan: Plan, warnings: list[str], done: str = "만들었습니다") -> str:
    """계획 머리 줄, 노드 표, 확인 노드 줄, 경고 줄을 빈 줄로 이은 글. done 은 머리 줄의 동사 (고칠 때 "고쳤습니다")."""
    head = f'계획 {plan.plan_id} "{plan.title}" 을 {done}. 노드 {len(plan.nodes)}개, 간선 {len(plan.edges)}개.'
    return "\n\n".join([head, _node_table(plan), _hitl_lines(plan), _warning_lines(warnings)])


def _node_table(plan: Plan) -> str:
    rows = ["| 노드 | 제목 | 종류 | 받는 산출물 |", "|---|---|---|---|"]
    for node in plan.nodes:
        received = ", ".join(str(node_id) for node_id in plan.prerequisites(node.node_id)) or "없음"
        rows.append(f"| {node.node_id} | {node.title} | {node.kind.value} | {received} |")
    return "\n".join(rows)


def _hitl_lines(plan: Plan) -> str:
    hitl_nodes = [node for node in plan.nodes if node.kind is NodeKind.HITL]
    if not hitl_nodes:
        return "확인 노드(HITL): 없음"
    lines = [f"- {node.node_id} {node.title}: {_what_to_confirm(node)}" for node in hitl_nodes]
    return "확인 노드(HITL):\n" + "\n".join(lines)


def _what_to_confirm(node: PlanNode) -> str:
    """확인받을 것: output_spec 의 '### 하는 일' 바로 아래 첫 줄."""
    after_heading = node.output_spec.split("### 하는 일\n", 1)[-1]
    return after_heading.strip().splitlines()[0] if after_heading.strip() else "(없음)"


def _warning_lines(warnings: list[str]) -> str:
    if not warnings:
        return "경고: 없음"
    return "경고:\n" + "\n".join(f"- {warning}" for warning in warnings)
