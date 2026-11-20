import logging
from typing import Annotated

from dishka.integrations.fastapi import DishkaSyncRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from task_plan_server.model.plan.plan_identity import PlanIdentity
from task_plan_server.model.plan.plan_status import PlanStatus
from task_plan_server.service.plan.dto.plan_create_command import PlanCreateCommand
from task_plan_server.service.plan.dto.plan_status_change_command import PlanStatusChangeCommand
from task_plan_server.service.plan.plan_reader import PlanReader
from task_plan_server.service.plan.usecase.plan_create_usecase import PlanCreateUsecase
from task_plan_server.service.plan.usecase.plan_status_change_usecase import (
    PlanStatusChangeUsecase,
)
from task_plan_server.service.plan_edge.dto.plan_edge_create_command import PlanEdgeCreateCommand
from task_plan_server.service.plan_edge.usecase.plan_edge_create_usecase import (
    PlanEdgeCreateUsecase,
)
from task_plan_server.service.plan_edge.usecase.plan_edge_delete_usecase import (
    PlanEdgeDeleteUsecase,
)
from task_plan_server.service.plan_node.dto.plan_node_create_command import PlanNodeCreateCommand
from task_plan_server.service.plan_node.dto.plan_node_update_command import PlanNodeUpdateCommand
from task_plan_server.service.plan_node.usecase.plan_node_create_usecase import (
    PlanNodeCreateUsecase,
)
from task_plan_server.service.plan_node.usecase.plan_node_delete_usecase import (
    PlanNodeDeleteUsecase,
)
from task_plan_server.service.plan_node.usecase.plan_node_update_usecase import (
    PlanNodeUpdateUsecase,
)

from .dto.edge_create_request import EdgeCreateRequest
from .dto.edge_create_response import EdgeCreateResponse
from .dto.node_create_request import NodeCreateRequest
from .dto.node_create_response import NodeCreateResponse
from .dto.node_update_request import NodeUpdateRequest
from .dto.plan_create_request import PlanCreateRequest
from .dto.plan_create_response import PlanCreateResponse
from .dto.plan_list_response import PlanListResponse, PlanSummaryResponse
from .dto.plan_response import PlanResponse
from .dto.plan_status_change_request import PlanStatusChangeRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plans", tags=["Plan"], route_class=DishkaSyncRoute)


@router.post("", summary="계획 만들기", status_code=status.HTTP_201_CREATED)
def create_plan(
    request: PlanCreateRequest, create_usecase: FromDishka[PlanCreateUsecase]
) -> PlanCreateResponse:
    command = PlanCreateCommand(
        title=request.title, request=request.request, persona_ids=tuple(request.persona_ids)
    )
    read = create_usecase.execute(command)
    return PlanCreateResponse.from_read(read)


@router.get("/{plan_id}", summary="계획 조회 (노드·간선 포함)")
def get_plan(plan_id: int, reader: FromDishka[PlanReader]) -> PlanResponse:
    return PlanResponse.from_read(reader.get_by_id(PlanIdentity(plan_id)))


@router.patch("/{plan_id}/status", summary="계획 상태 바꾸기 (순서 검사 없음)")
def change_plan_status(
    plan_id: int,
    request: PlanStatusChangeRequest,
    status_change_usecase: FromDishka[PlanStatusChangeUsecase],
) -> PlanResponse:
    command = PlanStatusChangeCommand(plan_id=plan_id, status=request.status)
    return PlanResponse.from_read(status_change_usecase.execute(command))


@router.post("/{plan_id}/nodes", summary="노드 하나 저장", status_code=status.HTTP_201_CREATED)
def create_node(
    plan_id: int,
    request: NodeCreateRequest,
    create_usecase: FromDishka[PlanNodeCreateUsecase],
) -> NodeCreateResponse:
    command = PlanNodeCreateCommand(
        plan_id=plan_id,
        title=request.title,
        kind=request.kind,
        persona_ids=tuple(request.persona_ids),
        output_spec=request.output_spec,
    )
    return NodeCreateResponse.from_read(create_usecase.execute(command))


@router.patch("/{plan_id}/nodes/{node_id}", summary="노드 하나 고치기 (바꿀 필드만)")
def update_node(
    plan_id: int,
    node_id: int,
    request: NodeUpdateRequest,
    update_usecase: FromDishka[PlanNodeUpdateUsecase],
) -> NodeCreateResponse:
    command = PlanNodeUpdateCommand(
        plan_id=plan_id,
        node_id=node_id,
        title=request.title,
        kind=request.kind,
        persona_ids=tuple(request.persona_ids) if request.persona_ids is not None else None,
        output_spec=request.output_spec,
        status=request.status,
    )
    return NodeCreateResponse.from_read(update_usecase.execute(command))


@router.delete(
    "/{plan_id}/nodes/{node_id}",
    summary="노드 하나 지우기 (닿은 간선도). 이미 없으면 아무것도 하지 않는다",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_node(
    plan_id: int, node_id: int, delete_usecase: FromDishka[PlanNodeDeleteUsecase]
) -> Response:
    delete_usecase.execute(plan_id, node_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{plan_id}/edges",
    summary="간선 하나 저장. 같은 간선이 있으면 그 간선을 돌려준다 (200)",
    status_code=status.HTTP_201_CREATED,
)
def create_edge(
    plan_id: int,
    request: EdgeCreateRequest,
    response: Response,
    create_usecase: FromDishka[PlanEdgeCreateUsecase],
) -> EdgeCreateResponse:
    command = PlanEdgeCreateCommand(
        plan_id=plan_id, from_node_id=request.from_node_id, to_node_id=request.to_node_id
    )
    result = create_usecase.execute(command)
    if not result.created:
        response.status_code = status.HTTP_200_OK
    return EdgeCreateResponse.from_read(result.edge)


@router.delete(
    "/{plan_id}/edges/{edge_id}",
    summary="간선 하나 지우기. 이미 없으면 아무것도 하지 않는다",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_edge(
    plan_id: int, edge_id: int, delete_usecase: FromDishka[PlanEdgeDeleteUsecase]
) -> Response:
    delete_usecase.execute(plan_id, edge_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", summary="계획 목록 (웹). 만든 시각 최근 순, 상태별 노드 수")
def list_plans(
    reader: FromDishka[PlanReader],
    plan_status: Annotated[
        PlanStatus | None, Query(alias="status", description="이 상태의 계획만")
    ] = None,
    limit: Annotated[int | None, Query(ge=1, le=200, description="최대 개수. 없으면 전부")] = None,
) -> PlanListResponse:
    summaries = reader.get_summaries(plan_status, limit)
    return PlanListResponse(plans=[PlanSummaryResponse.from_summary(s) for s in summaries])
