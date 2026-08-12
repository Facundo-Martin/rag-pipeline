from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(_app: FastAPI): # Note: We need to type _app as FastAPI so that it doesn't throw
    """
    Lifespan context manager handles startup and shutdown events.
    This is the modern way to handle application lifecycle in FastAPI.
    """
    # Startup: Initialize resources
    settings = get_settings()
    # TODO: Add db here

    print(f"Starting up {settings.app_name} [{settings.environment}]...")
    
    yield  # Application runs here

    # Shutdown: Clean up resources
    print(f"Shutting down {settings.app_name}...")

def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application instance.
    """
    settings = get_settings()

    # Create FastAPI instance with metadata
    application = FastAPI(
        title=settings.app_name,
        description="Production-ready FastAPI application",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TODO: Add custom middleware

    # TODO: Setup exception handlers

    # Include API routers
    application.include_router(
        api_v1_router,
        prefix="/api/v1",
    )

    return application


# Create application instance
app = create_application()