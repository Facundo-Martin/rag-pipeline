import structlog
from fastapi import APIRouter

logger = structlog.get_logger(__name__)

health_router = APIRouter()


@health_router.get("/health", summary="Liveness probe")
async def check_health() -> dict[str, str]:
    logger.info("Health probe check succeeded")
    return {"status": "healthy"}
