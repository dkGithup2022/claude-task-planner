import logging
from typing import Annotated

from dishka.integrations.fastapi import DishkaSyncRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from task_plan_server.model.memory.memory_identity import MemoryIdentity
from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.search_param import SearchParam
from task_plan_server.service.memory.dto.memory_create_command import MemoryCreateCommand
from task_plan_server.service.memory.dto.memory_update_command import MemoryUpdateCommand
from task_plan_server.service.memory.memory_reader import MemoryReader
from task_plan_server.service.memory.usecase.memory_create_usecase import MemoryCreateUsecase
from task_plan_server.service.memory.usecase.memory_delete_usecase import MemoryDeleteUsecase
from task_plan_server.service.memory.usecase.memory_update_usecase import MemoryUpdateUsecase

from .dto.memory_create_request import MemoryCreateRequest
from .dto.memory_id_response import MemoryIdResponse
from .dto.memory_list_response import MemoryListResponse
from .dto.memory_response import MemoryResponse
from .dto.memory_search_request import MemorySearchRequest
from .dto.memory_search_response import MemorySearchItem, MemorySearchResponse
from .dto.memory_update_request import MemoryUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memories", tags=["Memory"], route_class=DishkaSyncRoute)


@router.post("", summary="지식 하나 만들기", status_code=status.HTTP_201_CREATED)
def create_memory(
    request: MemoryCreateRequest, create_usecase: FromDishka[MemoryCreateUsecase]
) -> MemoryIdResponse:
    command = MemoryCreateCommand(
        kind=request.kind,
        theme=request.theme,
        body=request.body,
        persona_ids=tuple(request.persona_ids),
        sources=tuple(item.to_source() for item in request.source),
    )
    return MemoryIdResponse(memory_id=create_usecase.execute(command).memory_id)


@router.get("/{memory_id}", summary="지식 하나 조회")
def get_memory(memory_id: int, reader: FromDishka[MemoryReader]) -> MemoryResponse:
    return MemoryResponse.from_read(reader.get_by_id(MemoryIdentity(memory_id)))


@router.patch("/{memory_id}", summary="지식 고치기 (바꿀 필드만. 받은 것을 저장만 한다)")
def update_memory(
    memory_id: int,
    request: MemoryUpdateRequest,
    update_usecase: FromDishka[MemoryUpdateUsecase],
) -> MemoryIdResponse:
    command = MemoryUpdateCommand(
        memory_id=memory_id,
        kind=request.kind,
        theme=request.theme,
        body=request.body,
        persona_ids=tuple(request.persona_ids) if request.persona_ids is not None else None,
        sources=(
            tuple(item.to_source() for item in request.source)
            if request.source is not None
            else None
        ),
    )
    return MemoryIdResponse(memory_id=update_usecase.execute(command).memory_id)


@router.delete(
    "/{memory_id}",
    summary="지식 지우기. 없으면 404",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_memory(memory_id: int, delete_usecase: FromDishka[MemoryDeleteUsecase]) -> Response:
    delete_usecase.execute(MemoryIdentity(memory_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/search", summary="지식 검색 (검색어와 가까운 순)")
def search_memories(
    request: MemorySearchRequest, reader: FromDishka[MemoryReader]
) -> MemorySearchResponse:
    search_param = SearchParam(
        kind=request.kind,
        query=request.query,
        persona_ids=tuple(request.persona_ids),
        theme=request.theme,
        limit=request.limit,
    )
    hits = reader.search(search_param)
    return MemorySearchResponse(items=[MemorySearchItem.from_hit(hit) for hit in hits])


@router.get("", summary="지식 목록 (웹). 고친 시각 최근 순")
def list_memories(
    reader: FromDishka[MemoryReader],
    q: Annotated[str, Query(description="작업 이름이나 본문에 들어 있는 글자")] = "",
    kind: Annotated[MemoryKind | None, Query(description="이 종류만")] = None,
    persona_id: Annotated[int | None, Query(description="이 페르소나를 쓰는 지식만")] = None,
    limit: Annotated[int | None, Query(ge=1, le=200, description="최대 개수. 없으면 전부")] = None,
) -> MemoryListResponse:
    condition = MemoryListCondition(query=q, kind=kind, persona_id=persona_id, limit=limit)
    return MemoryListResponse.from_list(reader.get_list(condition))
