from abc import ABC, abstractmethod

from task_plan_server.model.plan.plan import Plan
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.model.plan.plan_summary import PlanSummary


class PlanRepository(ABC):
    @abstractmethod
    def save(self, plan: Plan) -> Plan:
        """계획 저장 (신규·수정). 참여 페르소나 순서를 지킨다. 저장한 계획을 id 와 함께 돌려준다."""

    @abstractmethod
    def find_write_by_id(self, identity: PlanIdentity) -> Plan | None:
        """계획 Write 모델 조회. 지운 계획은 없음으로 본다."""

    @abstractmethod
    def find_summaries(self, status: PlanStatus | None, limit: int | None) -> list[PlanSummary]:
        """계획 목록. 만든 시각 최근 순. 계획마다 지우지 않은 노드의 상태별 수. 지운 계획은 뺀다."""
