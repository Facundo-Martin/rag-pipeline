from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import api_v1_router
from src.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import setup_logging
from src.core.middleware import register_middleware

from src.infrastructure.postgres.session import init_db, close_db

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
):  # Note: We need to type _app as FastAPI so that it doesn't throw
    """
    Lifespan context manager handles startup and shutdown events.
    This is the modern way to handle application lifecycle in FastAPI.
    """
    # Startup: Initialize resources
    settings = get_settings()
    await init_db(settings.database_url)

    logger.info(
        "Starting up application",
        app_name=settings.app_name,
        environment=settings.environment,
    )

    yield  # Application runs here

    # Shutdown: Clean up resources
    await close_db()
    logger.info("Shutting down application", app_name=settings.app_name)


def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application instance.
    """
    settings = get_settings()

    # 1. Setup logging configuration first
    setup_logging(settings)

    # 2. Instantiate FastAPI
    application = FastAPI(
        title=settings.app_name,
        description="Production-ready FastAPI application",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # 3. Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 4. Register custom middleware
    register_middleware(application)

    # 5. Register exception handlers
    register_exception_handlers(application)

    # 6. Include API routers
    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
    )

    return application


# Create application instance
app = create_application()
