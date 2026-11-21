import pytest

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_planner.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_planner.port.plan_api.plan_api_error import PlanApiError
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError


def _new_node(title: str) -> NewNode:
    return NewNode(title, NodeKind.RESEARCH, (1,), "### 하는 일\n조사")


def test_should_save_plan_nodes_edges_and_read_them_back(mock_data_dir):
    writer = MockPlanApiWriter()
    plan = writer.create_plan(NewPlan("계획", "# 명령", (1,)))
    first = writer.add_node(plan.plan_id, _new_node("앞"))
    second = writer.add_node(plan.plan_id, _new_node("뒤"))
    edge = writer.add_edge(plan.plan_id, first.node_id, second.node_id)
    assert writer.add_edge(plan.plan_id, first.node_id, second.node_id) == edge  # 같은 간선은 하나

    saved = MockPlanApiReader().get_plan(plan.plan_id)
    assert saved.status == PlanStatus.DRAFTING
    assert [n.title for n in saved.nodes] == ["앞", "뒤"]
    assert saved.prerequisites(second.node_id) == (first.node_id,)
    assert (mock_data_dir / "plans" / f"{plan.plan_id}.json").exists()


def test_should_update_only_given_fields_and_delete_node_with_its_edges():
    writer = MockPlanApiWriter()
    plan = writer.create_plan(NewPlan("계획", "# 명령", (1,)))
    first = writer.add_node(plan.plan_id, _new_node("앞"))
    second = writer.add_node(plan.plan_id, _new_node("뒤"))
    writer.add_edge(plan.plan_id, first.node_id, second.node_id)

    changed = writer.update_node(plan.plan_id, first.node_id, NodeChange(status=PlanNodeStatus.DONE))
    assert changed.status == PlanNodeStatus.DONE and changed.title == "앞"

    writer.delete_node(plan.plan_id, first.node_id)
    saved = MockPlanApiReader().get_plan(plan.plan_id)
    assert [n.node_id for n in saved.nodes] == [second.node_id] and saved.edges == ()


def test_should_fail_on_missing_plan_or_missing_edge_node():
    with pytest.raises(PlanNotFoundError):
        MockPlanApiReader().get_plan(99)
    writer = MockPlanApiWriter()
    plan = writer.create_plan(NewPlan("계획", "# 명령", (1,)))
    with pytest.raises(PlanApiError):
        writer.add_edge(plan.plan_id, 1, 2)


def test_should_set_plan_status():
    writer = MockPlanApiWriter()
    plan = writer.create_plan(NewPlan("계획", "# 명령", (1,)))
    assert writer.set_plan_status(plan.plan_id, PlanStatus.REVIEWING).status == PlanStatus.REVIEWING
