from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from task_plan_server.my_logging import configure_logging

from .di import build_container
from .error_handlers import register_error_handlers
from .lifespan import lifespan
from .middleware.request_logging import RequestLoggingMiddleware
from .routers import register_routers
from .settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    configure_logging(settings.log_level, settings.effective_log_format)  # 가장 먼저

    app = FastAPI(title="task-plan-server", lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    register_error_handlers(app)
    register_routers(app)
    setup_dishka(build_container(), app)
    return app
