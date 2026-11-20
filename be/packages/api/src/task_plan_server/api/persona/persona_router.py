import logging

from dishka.integrations.fastapi import DishkaSyncRoute, FromDishka
from fastapi import APIRouter, Response, status

from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.service.persona.dto.persona_create_command import PersonaCreateCommand
from task_plan_server.service.persona.dto.persona_update_command import PersonaUpdateCommand
from task_plan_server.service.persona.persona_reader import PersonaReader
from task_plan_server.service.persona.usecase.persona_create_usecase import PersonaCreateUsecase
from task_plan_server.service.persona.usecase.persona_delete_usecase import PersonaDeleteUsecase
from task_plan_server.service.persona.usecase.persona_update_usecase import PersonaUpdateUsecase

from .dto.persona_create_request import PersonaCreateRequest
from .dto.persona_id_response import PersonaIdResponse
from .dto.persona_response import PersonaListResponse, PersonaResponse
from .dto.persona_update_request import PersonaUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personas", tags=["Persona"], route_class=DishkaSyncRoute)


@router.get("", summary="페르소나 목록 (지식 수, 계획 수 포함)")
def list_personas(reader: FromDishka[PersonaReader]) -> PersonaListResponse:
    return PersonaListResponse(
        personas=[PersonaResponse.from_read(read) for read in reader.get_all()]
    )


@router.post("", summary="페르소나 만들기. 같은 이름이면 409", status_code=status.HTTP_201_CREATED)
def create_persona(
    request: PersonaCreateRequest, create_usecase: FromDishka[PersonaCreateUsecase]
) -> PersonaIdResponse:
    command = PersonaCreateCommand(name=request.name, description=request.description)
    return PersonaIdResponse(persona_id=create_usecase.execute(command).persona_id)


@router.patch("/{persona_id}", summary="페르소나 이름·설명 고치기 (바꿀 필드만)")
def update_persona(
    persona_id: int,
    request: PersonaUpdateRequest,
    update_usecase: FromDishka[PersonaUpdateUsecase],
) -> PersonaIdResponse:
    command = PersonaUpdateCommand(
        persona_id=persona_id, name=request.name, description=request.description
    )
    return PersonaIdResponse(persona_id=update_usecase.execute(command).persona_id)


@router.delete(
    "/{persona_id}",
    summary="페르소나 지우기. 쓰는 지식이나 계획이 있으면 409",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_persona(persona_id: int, delete_usecase: FromDishka[PersonaDeleteUsecase]) -> Response:
    delete_usecase.execute(PersonaIdentity(persona_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
