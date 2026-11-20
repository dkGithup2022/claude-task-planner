from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.service.persona.persona_check import require_personas
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_create_command import PlanCreateCommand
from ..plan_writer import PlanWriter


class PlanCreateUsecase:
    """POST /api/plans 의 진입점. 만든 계획을 조회 모델로 돌려준다."""

    def __init__(
        self,
        tx: TransactionManager,
        plan_writer: PlanWriter,
        plan_repository: PlanRepository,
        persona_repository: PersonaRepository,
    ) -> None:
        self.tx = tx
        self._persona_repository = persona_repository
        self._plan_writer = plan_writer
        self._plan_repository = plan_repository

    @transactional
    def execute(self, command: PlanCreateCommand) -> PlanRead:
        require_personas(self._persona_repository, command.persona_ids)
        identity = self._plan_writer.create(command)
        plan = self._plan_repository.find_write_by_id(identity)
        if plan is None:
            raise PlanNotFoundException(f"plan not found right after create: {identity.plan_id}")
        return plan.to_read(nodes=(), edges=())  # 새 계획에는 노드와 간선이 없다
