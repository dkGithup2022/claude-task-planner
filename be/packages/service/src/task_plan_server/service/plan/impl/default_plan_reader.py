from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.model.plan.plan_summary import PlanSummary

from ..plan_reader import PlanReader


class DefaultPlanReader(PlanReader):
    """계획, 노드, 간선을 각 Repository 로 읽어 묶는다.

    트랜잭션을 열지 않으므로 세 번 읽기가 각자 짧은 트랜잭션이다.
    한 번에 읽어야 하면 부르는 쪽(쓰기 Usecase)이 트랜잭션을 연다.
    """

    def __init__(
        self,
        plan_repository: PlanRepository,
        plan_node_repository: PlanNodeRepository,
        plan_edge_repository: PlanEdgeRepository,
    ) -> None:
        self._plan_repository = plan_repository
        self._plan_node_repository = plan_node_repository
        self._plan_edge_repository = plan_edge_repository

    def get_by_id(self, identity: PlanIdentity) -> PlanRead:
        plan = self._plan_repository.find_write_by_id(identity)
        if plan is None:
            raise PlanNotFoundException(f"plan not found: {identity.plan_id}")
        nodes = self._plan_node_repository.find_by_plan_id(identity)
        edges = self._plan_edge_repository.find_by_plan_id(identity)
        return plan.to_read(tuple(nodes), tuple(edges))

    def get_summaries(self, status: PlanStatus | None, limit: int | None) -> list[PlanSummary]:
        return self._plan_repository.find_summaries(status, limit)
