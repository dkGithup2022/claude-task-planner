from typing import Self

from pydantic import BaseModel, Field

from task_plan_server.api.common.time_format import to_utc_text
from task_plan_server.model.plan.plan_node_counts import PlanNodeCounts
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.model.plan.plan_summary import PlanSummary


class NodeCountsResponse(BaseModel):
    todo: int = Field(description="할 일")
    running: int = Field(description="실행 중")
    done: int = Field(description="완료")
    failed: int = Field(description="실패")
    skipped: int = Field(description="건너뜀")
    total: int = Field(description="노드 수 합")

    @classmethod
    def from_counts(cls, counts: PlanNodeCounts) -> Self:
        return cls(
            todo=counts.todo,
            running=counts.running,
            done=counts.done,
            failed=counts.failed,
            skipped=counts.skipped,
            total=counts.total,
        )


class PlanSummaryResponse(BaseModel):
    """목록의 한 줄. 명령서, 노드, 간선은 넣지 않는다 (누르면 GET /api/plans/{plan_id})."""

    plan_id: int = Field(description="계획 id", examples=[11])
    title: str = Field(description="계획 제목")
    status: PlanStatus = Field(description="계획 상태. '실패' 는 없다 (실패한 노드 수로 본다)")
    persona_ids: list[int] = Field(description="참여 페르소나 id")
    created_at: str = Field(description="만든 시각 (UTC)", examples=["2026-11-20T04:16:15Z"])
    node_counts: NodeCountsResponse = Field(description="지우지 않은 노드의 상태별 수")

    @classmethod
    def from_summary(cls, summary: PlanSummary) -> Self:
        return cls(
            plan_id=summary.plan_id,
            title=summary.title,
            status=summary.status,
            persona_ids=list(summary.persona_ids),
            created_at=to_utc_text(summary.created_at),
            node_counts=NodeCountsResponse.from_counts(summary.node_counts),
        )


class PlanListResponse(BaseModel):
    plans: list[PlanSummaryResponse] = Field(description="만든 시각 최근 순")
