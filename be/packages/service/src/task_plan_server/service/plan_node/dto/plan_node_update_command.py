from dataclasses import dataclass

from task_plan_server.model.plan_node.node_kind import NodeKind
from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanNodeUpdateCommand:
    """노드 고치기. None 인 필드는 바꾸지 않는다. 상태 순서는 검사하지 않는다."""

    plan_id: int
    node_id: int
    title: str | None = None
    kind: NodeKind | None = None
    persona_ids: tuple[int, ...] | None = None
    output_spec: str | None = None
    status: PlanNodeStatus | None = None
