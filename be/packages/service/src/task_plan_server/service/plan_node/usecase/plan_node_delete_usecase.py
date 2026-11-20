from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..plan_node_writer import PlanNodeWriter


class PlanNodeDeleteUsecase:
    """DELETE /api/plans/{plan_id}/nodes/{node_id} 의 진입점.

    노드와 그 노드에 닿은 간선을 한 트랜잭션으로 지운다. 노드가 없거나 다른 계획의 노드면
    아무것도 하지 않는다 (API 문서: 이미 없으면 아무것도 하지 않는다).
    """

    def __init__(
        self,
        tx: TransactionManager,
        plan_node_repository: PlanNodeRepository,
        plan_node_writer: PlanNodeWriter,
        plan_edge_repository: PlanEdgeRepository,
    ) -> None:
        self.tx = tx
        self._plan_node_repository = plan_node_repository
        self._plan_node_writer = plan_node_writer
        self._plan_edge_repository = plan_edge_repository

    @transactional
    def execute(self, plan_id: int, node_id: int) -> None:
        identity = PlanNodeIdentity(node_id)
        node = self._plan_node_repository.find_write_by_id(identity)
        if node is None or node.plan_id != plan_id:
            return
        self._plan_node_writer.delete(identity)
        self._plan_edge_repository.delete_by_node_id(identity)
