from fastapi import APIRouter, FastAPI

from task_plan_server.api.memory.memory_router import router as memory_router
from task_plan_server.api.persona.persona_router import router as persona_router
from task_plan_server.api.plan.plan_router import router as plan_router

# add-api 스킬이 도메인별 router 를 여기에 등록한다.
ROUTERS: list[APIRouter] = [
    plan_router,
    memory_router,
    persona_router,
]


def register_routers(app: FastAPI) -> None:
    for router in ROUTERS:
        app.include_router(router)
