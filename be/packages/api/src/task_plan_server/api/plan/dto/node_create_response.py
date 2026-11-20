from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead
from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus


class NodeCreateResponse(BaseModel):
    node_id: int = Field(description="노드 id", examples=[56])
    status: PlanNodeStatus = Field(description="노드 상태. 만들 때는 todo")

    @classmethod
    def from_read(cls, read: PlanNodeRead) -> Self:
        return cls(node_id=read.node_id, status=read.status)
