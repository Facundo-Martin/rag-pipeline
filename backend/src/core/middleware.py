import time
import uuid

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import RequestResponseEndpoint

logger = structlog.get_logger(__name__)


async def add_process_time_and_request_id_header(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """
    Middleware that attaches X-Request-ID and X-Process-Time headers
    and binds correlation context to structlog.
    """
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    # Clear previous context and bind current request data
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000  # ms
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "HTTP request completed",
        status_code=response.status_code,
        process_time_ms=round(process_time, 2),
    )

    return response


def register_middleware(app: FastAPI) -> None:
    """
    Register custom middleware with the FastAPI application instance.
    """
    app.middleware("http")(add_process_time_and_request_id_header)
