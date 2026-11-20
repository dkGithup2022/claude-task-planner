import logging

from task_plan_server.exception.plan_edge.plan_edge_not_found_exception import (
    PlanEdgeNotFoundException,
)
from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.model.plan_edge.plan_edge import PlanEdge
from task_plan_server.model.plan_edge.plan_edge_identity import PlanEdgeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_edge_create_command import PlanEdgeCreateCommand
from ..plan_edge_writer import PlanEdgeWriter

logger = logging.getLogger(__name__)


class DefaultPlanEdgeWriter(PlanEdgeWriter):
    def __init__(self, tx: TransactionManager, repository: PlanEdgeRepository) -> None:
        self.tx = tx
        self._repository = repository

    @transactional
    def create(self, command: PlanEdgeCreateCommand) -> PlanEdgeIdentity:
        edge = PlanEdge.create(command.plan_id, command.from_node_id, command.to_node_id)
        saved = self._repository.save(edge)
        assert saved.edge_id is not None
        logger.info(
            "Plan edge created: edge_id=%s, %s -> %s",
            saved.edge_id,
            saved.from_node_id,
            saved.to_node_id,
        )
        return PlanEdgeIdentity(saved.edge_id)

    @transactional
    def delete(self, identity: PlanEdgeIdentity) -> None:
        if self._repository.find_write_by_id(identity) is None:
            raise PlanEdgeNotFoundException(f"plan edge not found: {identity.edge_id}")
        self._repository.delete_by_id(identity)
        logger.info("Plan edge deleted: edge_id=%s", identity.edge_id)
