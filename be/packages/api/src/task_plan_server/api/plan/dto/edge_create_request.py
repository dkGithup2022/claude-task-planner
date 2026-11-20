from pydantic import BaseModel, Field


class EdgeCreateRequest(BaseModel):
    from_node_id: int = Field(description="이 노드가 끝나야")
    to_node_id: int = Field(description="이 노드를 시작한다")
