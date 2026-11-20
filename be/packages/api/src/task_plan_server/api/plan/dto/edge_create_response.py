from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead


class EdgeCreateResponse(BaseModel):
    edge_id: int = Field(description="간선 id", examples=[108])

    @classmethod
    def from_read(cls, read: PlanEdgeRead) -> Self:
        return cls(edge_id=read.edge_id)
