from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.model.plan_edge.plan_edge_identity import PlanEdgeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..plan_edge_writer import PlanEdgeWriter


class PlanEdgeDeleteUsecase:
    """DELETE /api/plans/{plan_id}/edges/{edge_id} 의 진입점.

    간선이 없거나 다른 계획의 간선이면 아무것도 하지 않는다.
    API 문서: 이미 없으면 아무것도 하지 않는다.
    """

    def __init__(
        self,
        tx: TransactionManager,
        plan_edge_repository: PlanEdgeRepository,
        plan_edge_writer: PlanEdgeWriter,
    ) -> None:
        self.tx = tx
        self._plan_edge_repository = plan_edge_repository
        self._plan_edge_writer = plan_edge_writer

    @transactional
    def execute(self, plan_id: int, edge_id: int) -> None:
        identity = PlanEdgeIdentity(edge_id)
        edge = self._plan_edge_repository.find_write_by_id(identity)
        if edge is None or edge.plan_id != plan_id:
            return
        self._plan_edge_writer.delete(identity)
