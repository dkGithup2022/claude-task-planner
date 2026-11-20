from dishka import Provider, Scope, provide

from task_plan_server.infrastructure.plan.plan_repository import PlanRepository
from task_plan_server.persistence.plan.plan_entity_query import PlanEntityQuery
from task_plan_server.persistence.plan.plan_join_query import PlanJoinQuery
from task_plan_server.persistence.plan.plan_repository import DefaultPlanRepository
from task_plan_server.service.plan.impl.default_plan_reader import DefaultPlanReader
from task_plan_server.service.plan.impl.default_plan_writer import DefaultPlanWriter
from task_plan_server.service.plan.plan_reader import PlanReader
from task_plan_server.service.plan.plan_writer import PlanWriter
from task_plan_server.service.plan.usecase.plan_create_usecase import PlanCreateUsecase
from task_plan_server.service.plan.usecase.plan_status_change_usecase import (
    PlanStatusChangeUsecase,
)


class PlanProvider(Provider):
    scope = Scope.REQUEST

    entity_query = provide(PlanEntityQuery)
    join_query = provide(PlanJoinQuery)
    repository = provide(DefaultPlanRepository, provides=PlanRepository)
    reader = provide(DefaultPlanReader, provides=PlanReader)
    writer = provide(DefaultPlanWriter, provides=PlanWriter)
    create_usecase = provide(PlanCreateUsecase)
    status_change_usecase = provide(PlanStatusChangeUsecase)
