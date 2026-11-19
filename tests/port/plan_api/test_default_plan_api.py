import pytest

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.default_plan_api_reader import DefaultPlanApiReader
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.port.plan_api.plan_not_found_error import PlanNotFoundError

PLAN_BODY = {
    "plan_id": 1,
    "title": "계획",
    "request": "# 명령",
    "persona_ids": [1],
    "status": "drafting",
    "created_at": "2026-11-19T00:00:00Z",
    "nodes": [
        {
            "node_id": 11,
            "title": "조사",
            "kind": "research",
            "persona_ids": [1],
            "output_spec": "### 하는 일",
            "status": "done",
        }
    ],
    "edges": [],
}


def test_should_create_plan_and_nodes_edges_on_server(fake_api):
    fake_api.answer("POST", "/plans", {"plan_id": 1, "status": "drafting", "created_at": "2026-11-19T00:00:00Z"})
    fake_api.answer("GET", "/plans/1", PLAN_BODY)
    fake_api.answer("POST", "/plans/1/nodes", {"node_id": 12, "status": "todo"})
    fake_api.answer("POST", "/plans/1/edges", {"edge_id": 21})
    writer = plan_api_writer()

    assert writer.create_plan(NewPlan("계획", "# 명령", (1,))).nodes[0].node_id == 11
    node = writer.add_node(1, NewNode("정리", NodeKind.DOCUMENT, (1,), "### 하는 일"))
    assert (node.node_id, node.status) == (12, PlanNodeStatus.TODO)
    assert writer.add_edge(1, 11, 12).edge_id == 21

    sent = {(method, path): body for method, path, body in fake_api.requests}
    assert sent[("POST", "/plans/1/nodes")] == {
        "title": "정리",
        "kind": "document",
        "persona_ids": [1],
        "output_spec": "### 하는 일",
    }
    assert sent[("POST", "/plans/1/edges")] == {"from_node_id": 11, "to_node_id": 12}


def test_should_send_only_changed_fields_and_status(fake_api):
    fake_api.answer("PATCH", "/plans/1/nodes/11", {"node_id": 11, "status": "done"})
    fake_api.answer("PATCH", "/plans/1/status", {"plan_id": 1})
    fake_api.answer("GET", "/plans/1", PLAN_BODY)
    fake_api.answer("DELETE", "/plans/1/nodes/11", None)
    writer = plan_api_writer()

    assert writer.update_node(1, 11, NodeChange(status=PlanNodeStatus.DONE)).status == PlanNodeStatus.DONE
    writer.set_plan_status(1, PlanStatus.REVIEWING)
    writer.delete_node(1, 11)

    sent = {(method, path): body for method, path, body in fake_api.requests}
    assert sent[("PATCH", "/plans/1/nodes/11")] == {"status": "done"}
    assert sent[("PATCH", "/plans/1/status")] == {"status": "reviewing"}


def test_should_raise_not_found_when_server_says_404(fake_api):
    assert isinstance(plan_api_reader(), DefaultPlanApiReader)
    with pytest.raises(PlanNotFoundError):
        plan_api_reader().get_plan(99)
