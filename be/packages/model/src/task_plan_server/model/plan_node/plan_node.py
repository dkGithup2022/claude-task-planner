from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from task_plan_server.model.audit import utcnow

from .node_kind import NodeKind
from .plan_node_read import PlanNodeRead
from .plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanNode:
    """계획의 작업 하나. 앞 노드는 저장하지 않고 간선에서 계산한다 (CLI 가 한다)."""

    node_id: int | None
    plan_id: int
    title: str
    kind: NodeKind
    persona_ids: tuple[int, ...]  # 담당 페르소나. 확인 노드(HITL)면 보통 비어 있다
    output_spec: str  # 정의서 md. ### 하는 일, ### 산출물, ### 그 외 설명
    status: PlanNodeStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        plan_id: int,
        title: str,
        kind: NodeKind,
        persona_ids: tuple[int, ...],
        output_spec: str,
    ) -> Self:
        now = utcnow()
        return cls(
            None, plan_id, title, kind, persona_ids, output_spec, PlanNodeStatus.TODO, now, now
        )

    def with_update(
        self,
        title: str,
        kind: NodeKind,
        persona_ids: tuple[int, ...],
        output_spec: str,
        status: PlanNodeStatus,
    ) -> Self:
        """값을 바꾼 새 노드. 바꾸지 않는 필드는 부르는 쪽이 지금 값으로 채운다."""
        return replace(
            self,
            title=title,
            kind=kind,
            persona_ids=persona_ids,
            output_spec=output_spec,
            status=status,
            updated_at=utcnow(),
        )

    def to_read(self) -> PlanNodeRead:
        if self.node_id is None:
            raise ValueError("plan node must be persisted before to_read")
        return PlanNodeRead(
            self.node_id,
            self.plan_id,
            self.title,
            self.kind,
            self.persona_ids,
            self.output_spec,
            self.status,
            self.created_at,
            self.updated_at,
        )
