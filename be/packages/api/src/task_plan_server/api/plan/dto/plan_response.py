from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.api.common.time_format import to_utc_text
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.model.plan.plan_status import PlanStatus

from .edge_response import EdgeResponse
from .node_response import NodeResponse


class PlanResponse(BaseModel):
    """계획과 그 계획의 노드, 간선 전부. CLI 의 PlanJsonConverter.to_plan 이 읽는 모양."""

    plan_id: int = Field(description="계획 id", examples=[11])
    title: str = Field(description="계획 제목")
    request: str = Field(description="명령서 md")
    persona_ids: list[int] = Field(description="참여 페르소나 id")
    status: PlanStatus = Field(description="계획 상태")
    created_at: str = Field(description="만든 시각 (UTC)", examples=["2026-11-20T04:16:15Z"])
    nodes: list[NodeResponse] = Field(description="노드 전부 (node_id 순)")
    edges: list[EdgeResponse] = Field(description="간선 전부 (edge_id 순)")

    @classmethod
    def from_read(cls, read: PlanRead) -> Self:
        return cls(
            plan_id=read.plan_id,
            title=read.title,
            request=read.request,
            persona_ids=list(read.persona_ids),
            status=read.status,
            created_at=to_utc_text(read.created_at),
            nodes=[NodeResponse.from_read(node) for node in read.nodes],
            edges=[EdgeResponse.from_read(edge) for edge in read.edges],
        )
