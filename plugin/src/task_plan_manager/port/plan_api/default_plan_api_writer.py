"""계획 저장소 쓰기의 서버 구현. 데이터·API 문서의 계획·노드·간선 API 를 부른다.
응답이 id 와 상태만 주는 API 는, 요청한 값과 응답의 id 로 결과를 만들거나 계획을 다시 읽어 돌려준다."""

from __future__ import annotations

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_edge import PlanEdge
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.default_plan_api_reader import DefaultPlanApiReader
from task_plan_manager.port.plan_api.dto.new_node import NewNode
from task_plan_manager.port.plan_api.dto.new_plan import NewPlan
from task_plan_manager.port.plan_api.dto.node_change import NodeChange
from task_plan_manager.port.plan_api.plan_api_http import call_plan_api
from task_plan_manager.port.plan_api.plan_api_request_converter import PlanApiRequestConverter
from task_plan_manager.port.plan_api.plan_api_writer import PlanApiWriter


class DefaultPlanApiWriter(PlanApiWriter):
    def __init__(self) -> None:
        self.converter = PlanApiRequestConverter()
        self.reader = DefaultPlanApiReader()

    def create_plan(self, new_plan: NewPlan) -> Plan:
        # POST /plans 로 만들고, 받은 plan_id 로 계획을 다시 읽어 돌려준다
        created = call_plan_api("POST", "/plans", self.converter.to_new_plan_body(new_plan))
        return self.reader.get_plan(self.converter.to_id(created, "plan_id"))

    def add_node(self, plan_id: int, new_node: NewNode) -> PlanNode:
        # POST /plans/{plan_id}/nodes 로 저장하고, 요청한 값과 받은 node_id 로 노드를 만든다
        created = call_plan_api("POST", f"/plans/{plan_id}/nodes", self.converter.to_new_node_body(new_node))
        return PlanNode(
            node_id=self.converter.to_id(created, "node_id"),
            title=new_node.title,
            kind=new_node.kind,
            persona_ids=new_node.persona_ids,
            output_spec=new_node.output_spec,
            status=PlanNodeStatus(created.get("status") or PlanNodeStatus.TODO),
        )

    def add_edge(self, plan_id: int, from_node_id: int, to_node_id: int) -> PlanEdge:
        # POST /plans/{plan_id}/edges 로 저장하고 받은 edge_id 로 간선을 만든다
        body = {"from_node_id": from_node_id, "to_node_id": to_node_id}
        created = call_plan_api("POST", f"/plans/{plan_id}/edges", body)
        return PlanEdge(
            edge_id=self.converter.to_id(created, "edge_id"), from_node_id=from_node_id, to_node_id=to_node_id
        )

    def update_node(self, plan_id: int, node_id: int, change: NodeChange) -> PlanNode:
        # PATCH 로 바꿀 필드만 보내고, 계획을 다시 읽어 바뀐 노드를 돌려준다
        call_plan_api("PATCH", f"/plans/{plan_id}/nodes/{node_id}", self.converter.to_node_change_body(change))
        return self.reader.get_plan(plan_id).node(node_id)

    def delete_node(self, plan_id: int, node_id: int) -> None:
        # 서버가 그 노드에 닿은 간선도 함께 지운다
        call_plan_api("DELETE", f"/plans/{plan_id}/nodes/{node_id}")

    def delete_edge(self, plan_id: int, edge_id: int) -> None:
        call_plan_api("DELETE", f"/plans/{plan_id}/edges/{edge_id}")

    def set_plan_status(self, plan_id: int, status: PlanStatus) -> Plan:
        # PATCH /plans/{plan_id}/status (가안) 로 바꾸고 계획을 다시 읽어 돌려준다
        call_plan_api("PATCH", f"/plans/{plan_id}/status", self.converter.to_status_body(status))
        return self.reader.get_plan(plan_id)
