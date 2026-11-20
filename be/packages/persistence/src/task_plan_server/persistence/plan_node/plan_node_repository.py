from task_plan_server.exception.plan_node.plan_node_not_found_exception import (
    PlanNodeNotFoundException,
)
from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_node.plan_node import PlanNode
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.model.plan_node.plan_node_read import PlanNodeRead
from task_plan_server.transaction import TransactionManager, transactional

from .plan_node_entity import PlanNodeEntity, to_node_persona_entities
from .plan_node_entity_query import PlanNodeEntityQuery


class DefaultPlanNodeRepository(PlanNodeRepository):
    def __init__(self, tx: TransactionManager, entities: PlanNodeEntityQuery) -> None:
        self.tx = tx
        self._entities = entities

    @transactional
    def find_by_plan_id(self, plan_identity: PlanIdentity) -> list[PlanNodeRead]:
        entities = self._entities.find_by_plan_id_and_active(plan_identity.plan_id)
        return [entity.to_domain().to_read() for entity in entities]

    @transactional
    def save(self, node: PlanNode) -> PlanNode:
        if node.node_id is None:
            entity = self._entities.add(PlanNodeEntity.from_domain(node))
        else:
            found = self._entities.get(node.node_id)
            if found is None:
                raise PlanNodeNotFoundException(f"plan node not found: {node.node_id}")
            entity = found
            entity.title = node.title
            entity.kind = node.kind
            entity.personas = to_node_persona_entities(node.persona_ids)
            entity.output_spec = node.output_spec
            entity.status = node.status
            entity.updated_at = node.updated_at
            self._entities.flush()
        return entity.to_domain()

    @transactional
    def find_write_by_id(self, identity: PlanNodeIdentity) -> PlanNode | None:
        entity = self._entities.find_by_id_and_active(identity.node_id)
        return entity.to_domain() if entity is not None else None

    @transactional
    def delete_by_id(self, identity: PlanNodeIdentity) -> None:
        entity = self._entities.get(identity.node_id)
        if entity is None or entity.is_deleted:
            return
        entity.soft_delete()
        self._entities.flush()
