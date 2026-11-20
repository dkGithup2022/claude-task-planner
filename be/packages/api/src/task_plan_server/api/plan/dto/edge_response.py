from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead


class EdgeResponse(BaseModel):
    edge_id: int = Field(description="간선 id", examples=[102])
    from_node_id: int = Field(description="이 노드가 끝나야")
    to_node_id: int = Field(description="이 노드를 시작한다")

    @classmethod
    def from_read(cls, read: PlanEdgeRead) -> Self:
        return cls(edge_id=read.edge_id, from_node_id=read.from_node_id, to_node_id=read.to_node_id)
