from pydantic import BaseModel, Field

from task_plan_server.model.plan_node.node_kind import NodeKind


class NodeCreateRequest(BaseModel):
    title: str = Field(min_length=1, description="노드 제목")
    kind: NodeKind = Field(description="노드 종류")
    persona_ids: list[int] = Field(description="담당 페르소나 id. 확인 노드(hitl)면 보통 비어 있다")
    output_spec: str = Field(description="정의서 md")
