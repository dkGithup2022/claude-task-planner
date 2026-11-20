from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.exception.plan_node.plan_node_not_found_exception import (
    PlanNodeNotFoundException,
)
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead
from task_plan_server.service.persona.persona_check import require_personas
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_node_create_command import PlanNodeCreateCommand
from ..plan_node_writer import PlanNodeWriter


class PlanNodeCreateUsecase:
    """POST /api/plans/{plan_id}/nodes 의 진입점. 계획이 없으면 404."""

    def __init__(
        self,
        tx: TransactionManager,
        plan_repository: PlanRepository,
        plan_node_repository: PlanNodeRepository,
        plan_node_writer: PlanNodeWriter,
        persona_repository: PersonaRepository,
    ) -> None:
        self.tx = tx
        self._persona_repository = persona_repository
        self._plan_repository = plan_repository
        self._plan_node_repository = plan_node_repository
        self._plan_node_writer = plan_node_writer

    @transactional
    def execute(self, command: PlanNodeCreateCommand) -> PlanNodeRead:
        if self._plan_repository.find_write_by_id(PlanIdentity(command.plan_id)) is None:
            raise PlanNotFoundException(f"plan not found: {command.plan_id}")
        require_personas(self._persona_repository, command.persona_ids)
        identity = self._plan_node_writer.create(command)
        node = self._plan_node_repository.find_write_by_id(identity)
        if node is None:
            raise PlanNodeNotFoundException(f"plan node not found right after create: {identity}")
        return node.to_read()
