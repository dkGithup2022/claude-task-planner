from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead
from task_plan_server.service.persona.persona_check import require_personas
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_node_update_command import PlanNodeUpdateCommand
from ..plan_node_writer import PlanNodeWriter


class PlanNodeUpdateUsecase:
    """PATCH /api/plans/{plan_id}/nodes/{node_id} 의 진입점."""

    def __init__(
        self,
        tx: TransactionManager,
        plan_node_writer: PlanNodeWriter,
        persona_repository: PersonaRepository,
    ) -> None:
        self.tx = tx
        self._plan_node_writer = plan_node_writer
        self._persona_repository = persona_repository

    @transactional
    def execute(self, command: PlanNodeUpdateCommand) -> PlanNodeRead:
        require_personas(self._persona_repository, command.persona_ids)
        return self._plan_node_writer.update(command).to_read()
