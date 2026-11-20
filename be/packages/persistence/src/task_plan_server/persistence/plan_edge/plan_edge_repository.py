from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan_edge.plan_edge import PlanEdge
from task_plan_server.model.plan_edge.plan_edge_identity import PlanEdgeIdentity
from task_plan_server.model.plan_edge.plan_edge_read import PlanEdgeRead
from task_plan_server.model.plan_node.plan_node_identity import PlanNodeIdentity
from task_plan_server.transaction import TransactionManager, transactional

from .plan_edge_entity import PlanEdgeEntity
from .plan_edge_entity_query import PlanEdgeEntityQuery


class DefaultPlanEdgeRepository(PlanEdgeRepository):
    def __init__(self, tx: TransactionManager, entities: PlanEdgeEntityQuery) -> None:
        self.tx = tx
        self._entities = entities

    @transactional
    def find_by_plan_id(self, plan_identity: PlanIdentity) -> list[PlanEdgeRead]:
        entities = self._entities.find_by_plan_id_and_active(plan_identity.plan_id)
        return [entity.to_domain().to_read() for entity in entities]

    @transactional
    def delete_by_node_id(self, node_identity: PlanNodeIdentity) -> None:
        entities = self._entities.find_by_node_id_and_active(node_identity.node_id)
        for entity in entities:
            entity.soft_delete()
        if entities:
            self._entities.flush()

    @transactional
    def save(self, edge: PlanEdge) -> PlanEdge:
        if edge.edge_id is not None:
            raise ValueError("plan edges are never updated; save only new edges")
        return self._entities.add(PlanEdgeEntity.from_domain(edge)).to_domain()

    @transactional
    def find_by_ends(
        self, plan_identity: PlanIdentity, from_node_id: int, to_node_id: int
    ) -> PlanEdge | None:
        entity = self._entities.find_by_ends_and_active(
            plan_identity.plan_id, from_node_id, to_node_id
        )
        return entity.to_domain() if entity is not None else None

    @transactional
    def find_write_by_id(self, identity: PlanEdgeIdentity) -> PlanEdge | None:
        entity = self._entities.find_by_id_and_active(identity.edge_id)
        return entity.to_domain() if entity is not None else None

    @transactional
    def delete_by_id(self, identity: PlanEdgeIdentity) -> None:
        entity = self._entities.get(identity.edge_id)
        if entity is None or entity.is_deleted:
            return
        entity.soft_delete()
        self._entities.flush()
