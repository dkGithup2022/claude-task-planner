from dishka import Provider, Scope, provide

from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository
from task_plan_server.persistence.persona.persona_entity_query import PersonaEntityQuery
from task_plan_server.persistence.persona.persona_join_query import PersonaJoinQuery
from task_plan_server.persistence.persona.persona_repository import DefaultPersonaRepository
from task_plan_server.service.persona.impl.default_persona_reader import DefaultPersonaReader
from task_plan_server.service.persona.impl.default_persona_writer import DefaultPersonaWriter
from task_plan_server.service.persona.persona_reader import PersonaReader
from task_plan_server.service.persona.persona_writer import PersonaWriter
from task_plan_server.service.persona.usecase.persona_create_usecase import PersonaCreateUsecase
from task_plan_server.service.persona.usecase.persona_delete_usecase import PersonaDeleteUsecase
from task_plan_server.service.persona.usecase.persona_update_usecase import PersonaUpdateUsecase


class PersonaProvider(Provider):
    scope = Scope.REQUEST

    entity_query = provide(PersonaEntityQuery)
    join_query = provide(PersonaJoinQuery)
    repository = provide(DefaultPersonaRepository, provides=PersonaRepository)
    reader = provide(DefaultPersonaReader, provides=PersonaReader)
    writer = provide(DefaultPersonaWriter, provides=PersonaWriter)
    create_usecase = provide(PersonaCreateUsecase)
    update_usecase = provide(PersonaUpdateUsecase)
    delete_usecase = provide(PersonaDeleteUsecase)
