from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from task_plan_server.model.audit import utcnow
from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead

from .plan_node_counts import PlanNodeCounts
from .plan_read import PlanRead
from .plan_status import PlanStatus
from .plan_summary import PlanSummary


@dataclass(frozen=True, slots=True)
class Plan:
    """작업 계획. 노드와 간선은 각자의 도메인에 저장하고, 조회할 때 묶는다."""

    plan_id: int | None
    title: str
    request: str  # 명령서 md
    persona_ids: tuple[int, ...]  # 참여 페르소나
    status: PlanStatus
    created_at: datetime  # API 응답에 나간다
    updated_at: datetime  # 서버 안에만 둔다

    @classmethod
    def create(cls, title: str, request: str, persona_ids: tuple[int, ...]) -> Self:
        now = utcnow()
        return cls(None, title, request, persona_ids, PlanStatus.DRAFTING, now, now)

    def with_status(self, status: PlanStatus) -> Self:
        """상태를 바꾼 새 계획. 바꾸는 순서는 검사하지 않는다."""
        return replace(self, status=status, updated_at=utcnow())

    def to_read(self, nodes: tuple[PlanNodeRead, ...], edges: tuple[PlanEdgeRead, ...]) -> PlanRead:
        plan_id = self._persisted_id()
        return PlanRead(
            plan_id,
            self.title,
            self.request,
            self.persona_ids,
            self.status,
            nodes,
            edges,
            self.created_at,
            self.updated_at,
        )

    def to_summary(self, node_counts: PlanNodeCounts) -> PlanSummary:
        plan_id = self._persisted_id()
        return PlanSummary(
            plan_id,
            self.title,
            self.status,
            self.persona_ids,
            node_counts,
            self.created_at,
            self.updated_at,
        )

    def _persisted_id(self) -> int:
        if self.plan_id is None:
            raise ValueError("plan must be persisted before to_read")
        return self.plan_id
