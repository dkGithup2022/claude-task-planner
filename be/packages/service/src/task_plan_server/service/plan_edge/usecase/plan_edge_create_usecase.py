from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.exception.plan_edge.plan_edge_end_not_in_plan_exception import (
    PlanEdgeEndNotInPlanException,
)
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_edge_create_command import PlanEdgeCreateCommand
from ..dto.plan_edge_created import PlanEdgeCreated
from ..plan_edge_writer import PlanEdgeWriter


class PlanEdgeCreateUsecase:
    """POST /api/plans/{plan_id}/edges 의 진입점.

    계획이 없으면 404, 양 끝 노드가 그 계획에 없으면 400. 같은 간선이 있으면 그것을 돌려준다.
    자기 자신을 잇는 간선과 순환은 막지 않는다 (CLI 가 확정·실행 전에 본다).
    """

    def __init__(
        self,
        tx: TransactionManager,
        plan_repository: PlanRepository,
        plan_node_repository: PlanNodeRepository,
        plan_edge_repository: PlanEdgeRepository,
        plan_edge_writer: PlanEdgeWriter,
    ) -> None:
        self.tx = tx
        self._plan_repository = plan_repository
        self._plan_node_repository = plan_node_repository
        self._plan_edge_repository = plan_edge_repository
        self._plan_edge_writer = plan_edge_writer

    @transactional
    def execute(self, command: PlanEdgeCreateCommand) -> PlanEdgeCreated:
        plan_identity = PlanIdentity(command.plan_id)
        if self._plan_repository.find_write_by_id(plan_identity) is None:
            raise PlanNotFoundException(f"plan not found: {command.plan_id}")
        for node_id in (command.from_node_id, command.to_node_id):
            node = self._plan_node_repository.find_write_by_id(PlanNodeIdentity(node_id))
            if node is None or node.plan_id != command.plan_id:
                raise PlanEdgeEndNotInPlanException(command.plan_id, node_id)

        existing = self._plan_edge_repository.find_by_ends(
            plan_identity, command.from_node_id, command.to_node_id
        )
        if existing is not None:
            return PlanEdgeCreated(existing.to_read(), created=False)

        identity = self._plan_edge_writer.create(command)
        created = self._plan_edge_repository.find_by_ends(
            plan_identity, command.from_node_id, command.to_node_id
        )
        assert created is not None and created.edge_id == identity.edge_id
        return PlanEdgeCreated(created.to_read(), created=True)
