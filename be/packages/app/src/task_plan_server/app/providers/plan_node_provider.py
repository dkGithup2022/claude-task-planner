from dishka import Provider, Scope, provide

from task_plan_server.infrastructure.plan_node.plan_node_repository import PlanNodeRepository
from task_plan_server.persistence.plan_node.plan_node_entity_query import PlanNodeEntityQuery
from task_plan_server.persistence.plan_node.plan_node_repository import DefaultPlanNodeRepository
from task_plan_server.service.plan_node.impl.default_plan_node_writer import DefaultPlanNodeWriter
from task_plan_server.service.plan_node.plan_node_writer import PlanNodeWriter
from task_plan_server.service.plan_node.usecase.plan_node_create_usecase import (
    PlanNodeCreateUsecase,
)
from task_plan_server.service.plan_node.usecase.plan_node_delete_usecase import (
    PlanNodeDeleteUsecase,
)
from task_plan_server.service.plan_node.usecase.plan_node_update_usecase import (
    PlanNodeUpdateUsecase,
)


class PlanNodeProvider(Provider):
    scope = Scope.REQUEST

    entity_query = provide(PlanNodeEntityQuery)
    repository = provide(DefaultPlanNodeRepository, provides=PlanNodeRepository)
    writer = provide(DefaultPlanNodeWriter, provides=PlanNodeWriter)
    create_usecase = provide(PlanNodeCreateUsecase)
    update_usecase = provide(PlanNodeUpdateUsecase)
    delete_usecase = provide(PlanNodeDeleteUsecase)
