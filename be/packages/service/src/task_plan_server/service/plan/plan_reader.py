from abc import ABC, abstractmethod

from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.model.plan.plan_summary import PlanSummary


class PlanReader(ABC):
    @abstractmethod
    def get_by_id(self, identity: PlanIdentity) -> PlanRead:
        """계획과 그 계획의 노드, 간선 전부. 없으면 PlanNotFoundException."""

    @abstractmethod
    def get_summaries(self, status: PlanStatus | None, limit: int | None) -> list[PlanSummary]:
        """계획 목록. 만든 시각 최근 순. 상태별 노드 수를 담는다. 없으면 []."""
