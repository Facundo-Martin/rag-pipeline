import structlog
from fastapi import APIRouter, Response, status

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.dependencies import DbSession

logger = structlog.get_logger(__name__)

health_router = APIRouter()


@health_router.get("/health", summary="Liveness probe")
async def check_health() -> dict[str, str]:
    logger.info("Health probe check succeeded")
    return {"status": "healthy"}

@health_router.get("/ready", summary="Readiness probe")
async def check_readiness(db: DbSession, response: Response) -> dict[str, str]:
    """Deeper check to prove the API can communicate with its dependencies."""
    try:
        # Ping the database
        await db.execute(text("SELECT 1"))
        logger.info("Readiness probe check succeeded - DB connected")
        return {"status": "ready", "database": "connected"}
        
    except SQLAlchemyError as e:
        logger.error("Readiness probe failed", error=str(e))
        
        # Return a 503 so load balancers know NOT to route traffic here yet
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database": "disconnected"}