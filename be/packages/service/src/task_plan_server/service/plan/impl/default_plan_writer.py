import logging

from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.model.plan.plan import Plan
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_create_command import PlanCreateCommand
from ..dto.plan_status_change_command import PlanStatusChangeCommand
from ..plan_writer import PlanWriter

logger = logging.getLogger(__name__)


class DefaultPlanWriter(PlanWriter):
    def __init__(self, tx: TransactionManager, repository: PlanRepository) -> None:
        self.tx = tx
        self._repository = repository

    @transactional
    def create(self, command: PlanCreateCommand) -> PlanIdentity:
        plan = Plan.create(command.title, command.request, command.persona_ids)
        saved = self._repository.save(plan)
        assert saved.plan_id is not None
        logger.info("Plan created: id=%s", saved.plan_id)
        return PlanIdentity(saved.plan_id)

    @transactional
    def change_status(self, command: PlanStatusChangeCommand) -> Plan:
        existing = self._repository.find_write_by_id(PlanIdentity(command.plan_id))
        if existing is None:
            raise PlanNotFoundException(f"plan not found: {command.plan_id}")
        saved = self._repository.save(existing.with_status(command.status))
        logger.info(
            "Plan status changed: id=%s, %s -> %s", command.plan_id, existing.status, saved.status
        )
        return saved
