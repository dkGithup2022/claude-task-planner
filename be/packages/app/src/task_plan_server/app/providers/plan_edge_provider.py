from dishka import Provider, Scope, provide

from task_plan_server.infrastructure.plan_edge.plan_edge_repository import PlanEdgeRepository
from task_plan_server.persistence.plan_edge.plan_edge_entity_query import PlanEdgeEntityQuery
from task_plan_server.persistence.plan_edge.plan_edge_repository import DefaultPlanEdgeRepository
from task_plan_server.service.plan_edge.impl.default_plan_edge_writer import DefaultPlanEdgeWriter
from task_plan_server.service.plan_edge.plan_edge_writer import PlanEdgeWriter
from task_plan_server.service.plan_edge.usecase.plan_edge_create_usecase import (
    PlanEdgeCreateUsecase,
)
from task_plan_server.service.plan_edge.usecase.plan_edge_delete_usecase import (
    PlanEdgeDeleteUsecase,
)


class PlanEdgeProvider(Provider):
    scope = Scope.REQUEST

    entity_query = provide(PlanEdgeEntityQuery)
    repository = provide(DefaultPlanEdgeRepository, provides=PlanEdgeRepository)
    writer = provide(DefaultPlanEdgeWriter, provides=PlanEdgeWriter)
    create_usecase = provide(PlanEdgeCreateUsecase)
    delete_usecase = provide(PlanEdgeDeleteUsecase)
