import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from task_plan_server.exception.domain_exception import DomainException

from .error_response import ErrorResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        message = ", ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        logger.info("Validation failed: %s", message)
        body = ErrorResponse(status=400, error="ValidationFailed", message=message)
        return JSONResponse(status_code=400, content=body.model_dump())

    @app.exception_handler(DomainException)
    def handle_domain(request: Request, exc: DomainException) -> JSONResponse:
        status = getattr(exc, "http_status_code", None)
        client_message = getattr(exc, "http_error_message", None)
        if status is not None and client_message is not None:
            logger.warning("Domain error [%s] - %s: %s", status, type(exc).__name__, exc.detail)
            body = ErrorResponse(status=status, error=type(exc).__name__, message=client_message)
            return JSONResponse(status_code=status, content=body.model_dump())
        logger.error(
            "Unhandled domain error - %s: %s", type(exc).__name__, exc.detail, exc_info=exc
        )
        body = ErrorResponse(status=500, error=type(exc).__name__, message="Internal server error")
        return JSONResponse(status_code=500, content=body.model_dump())

    @app.exception_handler(Exception)
    def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unexpected error: %s", exc, exc_info=exc)
        body = ErrorResponse(
            status=500, error="InternalServerError", message="Internal server error"
        )
        return JSONResponse(status_code=500, content=body.model_dump())
