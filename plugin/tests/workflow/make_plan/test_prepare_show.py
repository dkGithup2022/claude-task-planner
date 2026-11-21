"""prepare_show: 보일 글 모양과 검토 중으로 바꾸는 규칙."""

import pytest

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_edge import PlanEdge
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_planner.workflow.make_plan.prepare_show.plan_not_showable_error import PlanNotShowableError
from task_planner.workflow.make_plan.prepare_show.plan_summary import build_summary
from task_planner.workflow.make_plan.prepare_show.prepare_show_task import _move_to_reviewing


def _node(node_id: int, title: str, kind: NodeKind = NodeKind.DOCUMENT) -> PlanNode:
    return PlanNode(
        node_id, title, kind, (), f"### 하는 일\n{title} 결과를 확인받는다\n\n### 산출물", PlanNodeStatus.TODO
    )


def test_should_show_node_table_hitl_and_warnings():
    nodes = (_node(1, "배합 설계"), _node(2, "굽기 조건"), _node(3, "맛 확인", NodeKind.HITL))
    edges = (PlanEdge(1, 1, 2), PlanEdge(2, 1, 3), PlanEdge(3, 2, 3))
    plan = Plan(1, "밤만쥬", "# 명령", (1,), PlanStatus.REVIEWING, "2026-11-19T00:00:00Z", nodes, edges)

    summary = build_summary(plan, ["노드 상한 40개에 닿음"])

    assert summary.startswith(
        '계획 1 "밤만쥬" 을 만들었습니다. 노드 3개, 간선 3개.\n\n| 노드 | 제목 | 종류 | 받는 산출물 |'
    )
    assert "| 1 | 배합 설계 | document | 없음 |" in summary
    assert "| 3 | 맛 확인 | hitl | 1, 2 |" in summary
    assert "확인 노드(HITL):\n- 3 맛 확인: 맛 확인 결과를 확인받는다" in summary
    assert summary.endswith("경고:\n- 노드 상한 40개에 닿음")


def test_should_move_drafting_to_reviewing_and_keep_reviewing():
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan("계획", "# 명령", (1,))).plan_id
    assert _move_to_reviewing(plan_id).status is PlanStatus.REVIEWING
    assert _move_to_reviewing(plan_id).status is PlanStatus.REVIEWING  # 이미 검토 중이면 그대로


def test_should_refuse_plan_that_is_already_approved():
    writer = MockPlanApiWriter()
    plan_id = writer.create_plan(NewPlan("계획", "# 명령", (1,))).plan_id
    writer.set_plan_status(plan_id, PlanStatus.APPROVED)
    with pytest.raises(PlanNotShowableError):
        _move_to_reviewing(plan_id)
