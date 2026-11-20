from task_plan_server.exception.plan.plan_not_found_exception import PlanNotFoundException
from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.model.plan.plan import Plan
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_node_counts import PlanNodeCounts
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.model.plan.plan_summary import PlanSummary
from task_plan_server.transaction import TransactionManager, transactional

from .plan_entity import PlanEntity, to_persona_entities
from .plan_entity_query import PlanEntityQuery
from .plan_join_query import PlanJoinQuery


class DefaultPlanRepository(PlanRepository):
    def __init__(
        self, tx: TransactionManager, entities: PlanEntityQuery, joins: PlanJoinQuery
    ) -> None:
        self.tx = tx
        self._entities = entities
        self._joins = joins

    @transactional
    def save(self, plan: Plan) -> Plan:
        if plan.plan_id is None:
            entity = self._entities.add(PlanEntity.from_domain(plan))
        else:
            found = self._entities.get(plan.plan_id)
            if found is None:
                raise PlanNotFoundException(f"plan not found: {plan.plan_id}")
            entity = found
            entity.title = plan.title
            entity.request = plan.request
            entity.status = plan.status
            entity.personas = to_persona_entities(plan.persona_ids)
            entity.updated_at = plan.updated_at
            self._entities.flush()
        return entity.to_domain()

    @transactional
    def find_write_by_id(self, identity: PlanIdentity) -> Plan | None:
        entity = self._entities.find_by_id_and_active(identity.plan_id)
        return entity.to_domain() if entity is not None else None

    @transactional
    def find_summaries(self, status: PlanStatus | None, limit: int | None) -> list[PlanSummary]:
        entities = self._entities.find_all_and_active(status, limit)
        rows = self._joins.count_nodes_by_status([entity.id for entity in entities])
        counts = {
            row.plan_id: PlanNodeCounts(row.todo, row.running, row.done, row.failed, row.skipped)
            for row in rows
        }
        empty = PlanNodeCounts(0, 0, 0, 0, 0)
        return [entity.to_domain().to_summary(counts.get(entity.id, empty)) for entity in entities]
