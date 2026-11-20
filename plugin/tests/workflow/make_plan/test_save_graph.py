"""save_graph: mock 계획 저장소에 노드·간선을 저장하고, 다시 수행하면 앞선 노드를 지운다."""

import pytest

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.mock_plan_api_reader import MockPlanApiReader
from task_plan_manager.port.plan_api.mock_plan_api_writer import MockPlanApiWriter
from task_plan_manager.workflow.make_plan.split_plan.save_graph.plan_not_drafting_error import PlanNotDraftingError
from task_plan_manager.workflow.make_plan.split_plan.save_graph.save_graph import save_graph
from task_plan_manager.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_plan_manager.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft


def _draft(local_id: str, output_spec: str = "### 하는 일\n한다") -> NodeDraft:
    return NodeDraft(local_id, f"작업 {local_id}", NodeKind.DOCUMENT, (1,), output_spec, f"계획 / {local_id}", ())


DRAFTS = (_draft("n1"), _draft("n2", "### 그 외 설명\n- 하나\\n- 둘"), _draft("n3"))
EDGES = (EdgeDraft("n1", "n2"), EdgeDraft("n1", "n3"))


def _new_plan() -> int:
    return MockPlanApiWriter().create_plan(NewPlan("계획", "# 명령", (1,))).plan_id


def test_should_save_nodes_then_edges_with_server_ids():
    plan_id = _new_plan()
    saved = save_graph(plan_id, DRAFTS, EDGES, MockPlanApiReader(), MockPlanApiWriter())

    plan = MockPlanApiReader().get_plan(plan_id)
    assert [node.title for node in plan.nodes] == ["작업 n1", "작업 n2", "작업 n3"]
    assert saved.node_ids == {"n1": plan.nodes[0].node_id, "n2": plan.nodes[1].node_id, "n3": plan.nodes[2].node_id}
    assert plan.prerequisites(saved.node_ids["n2"]) == (saved.node_ids["n1"],)
    assert saved.edge_count == 2 and saved.removed_node_count == 0
    assert plan.node(saved.node_ids["n2"]).output_spec == "### 그 외 설명\n- 하나\n- 둘"  # 글자 \n 을 줄바꿈으로


def test_should_replace_previous_nodes_when_run_again():
    plan_id = _new_plan()
    save_graph(plan_id, DRAFTS, EDGES, MockPlanApiReader(), MockPlanApiWriter())
    again = save_graph(plan_id, DRAFTS[:2], EDGES[:1], MockPlanApiReader(), MockPlanApiWriter())

    plan = MockPlanApiReader().get_plan(plan_id)
    assert again.removed_node_count == 3
    assert [node.title for node in plan.nodes] == ["작업 n1", "작업 n2"] and len(plan.edges) == 1


def test_should_not_touch_plan_that_is_not_drafting():
    plan_id = _new_plan()
    MockPlanApiWriter().set_plan_status(plan_id, PlanStatus.REVIEWING)
    with pytest.raises(PlanNotDraftingError):
        save_graph(plan_id, DRAFTS, EDGES, MockPlanApiReader(), MockPlanApiWriter())
    assert MockPlanApiReader().get_plan(plan_id).nodes == ()
