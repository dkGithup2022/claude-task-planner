import logging

from task_plan_server.exception.plan_node.plan_node_not_found_exception import (
    PlanNodeNotFoundException,
)
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan_node.plan_node import PlanNode
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_node_create_command import PlanNodeCreateCommand
from ..dto.plan_node_update_command import PlanNodeUpdateCommand
from ..plan_node_writer import PlanNodeWriter

logger = logging.getLogger(__name__)


class DefaultPlanNodeWriter(PlanNodeWriter):
    def __init__(self, tx: TransactionManager, repository: PlanNodeRepository) -> None:
        self.tx = tx
        self._repository = repository

    @transactional
    def create(self, command: PlanNodeCreateCommand) -> PlanNodeIdentity:
        node = PlanNode.create(
            command.plan_id, command.title, command.kind, command.persona_ids, command.output_spec
        )
        saved = self._repository.save(node)
        assert saved.node_id is not None
        logger.info("Plan node created: plan_id=%s, node_id=%s", saved.plan_id, saved.node_id)
        return PlanNodeIdentity(saved.node_id)

    @transactional
    def update(self, command: PlanNodeUpdateCommand) -> PlanNode:
        existing = self._repository.find_write_by_id(PlanNodeIdentity(command.node_id))
        if existing is None or existing.plan_id != command.plan_id:
            raise PlanNodeNotFoundException(
                f"plan node not found: plan_id={command.plan_id}, node_id={command.node_id}"
            )
        updated = existing.with_update(
            title=_or(command.title, existing.title),
            kind=_or(command.kind, existing.kind),
            persona_ids=_or(command.persona_ids, existing.persona_ids),
            output_spec=_or(command.output_spec, existing.output_spec),
            status=_or(command.status, existing.status),
        )
        saved = self._repository.save(updated)
        logger.info("Plan node updated: node_id=%s, status=%s", saved.node_id, saved.status)
        return saved

    @transactional
    def delete(self, identity: PlanNodeIdentity) -> None:
        if self._repository.find_write_by_id(identity) is None:
            raise PlanNodeNotFoundException(f"plan node not found: {identity.node_id}")
        self._repository.delete_by_id(identity)
        logger.info("Plan node deleted: node_id=%s", identity.node_id)


def _or[T](value: T | None, current: T) -> T:
    """보낸 값이 있으면 그 값, 없으면 지금 값."""
    return current if value is None else value
