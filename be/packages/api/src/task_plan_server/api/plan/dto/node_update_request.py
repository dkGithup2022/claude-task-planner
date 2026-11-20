from pydantic import BaseModel, Field

from task_plan_server.model.plan_node.node_kind import NodeKind
from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus


class NodeUpdateRequest(BaseModel):
    """바꿀 필드만 보낸다. 빠지거나 null 인 필드는 바꾸지 않는다."""

    title: str | None = Field(default=None, min_length=1, description="노드 제목")
    kind: NodeKind | None = Field(default=None, description="노드 종류")
    persona_ids: list[int] | None = Field(default=None, description="담당 페르소나 id")
    output_spec: str | None = Field(default=None, description="정의서 md")
    status: PlanNodeStatus | None = Field(
        default=None, description="노드 상태. 순서는 검사하지 않는다"
    )
