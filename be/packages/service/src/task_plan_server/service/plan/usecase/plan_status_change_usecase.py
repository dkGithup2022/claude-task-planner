from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_read import PlanRead
from task_plan_server.transaction import TransactionManager, transactional

from ..dto.plan_status_change_command import PlanStatusChangeCommand
from ..plan_reader import PlanReader
from ..plan_writer import PlanWriter


class PlanStatusChangeUsecase:
    """PATCH /api/plans/{plan_id}/status 의 진입점. 바꾼 뒤 노드·간선까지 다시 읽어 돌려준다."""

    def __init__(
        self, tx: TransactionManager, plan_writer: PlanWriter, plan_reader: PlanReader
    ) -> None:
        self.tx = tx
        self._plan_writer = plan_writer
        self._plan_reader = plan_reader

    @transactional
    def execute(self, command: PlanStatusChangeCommand) -> PlanRead:
        self._plan_writer.change_status(command)
        return self._plan_reader.get_by_id(PlanIdentity(command.plan_id))
