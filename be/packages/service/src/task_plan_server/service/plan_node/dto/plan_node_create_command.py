from dataclasses import dataclass

from task_plan_server.model.plan_node.node_kind import NodeKind


@dataclass(frozen=True, slots=True)
class PlanNodeCreateCommand:
    plan_id: int
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]
    output_spec: str  # 정의서 md
