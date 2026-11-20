from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.plan_node.node_kind import NodeKind
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead
from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus


class NodeResponse(BaseModel):
    node_id: int = Field(description="노드 id", examples=[54])
    title: str = Field(description="노드 제목")
    kind: NodeKind = Field(description="노드 종류")
    persona_ids: list[int] = Field(description="담당 페르소나 id. 확인 노드(hitl)면 보통 비어 있다")
    output_spec: str = Field(description="정의서 md")
    status: PlanNodeStatus = Field(description="노드 상태")

    @classmethod
    def from_read(cls, read: PlanNodeRead) -> Self:
        return cls(
            node_id=read.node_id,
            title=read.title,
            kind=read.kind,
            persona_ids=list(read.persona_ids),
            output_spec=read.output_spec,
            status=read.status,
        )
