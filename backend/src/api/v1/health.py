from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health", summary="Liveness probe")
async def check_health() -> dict[str, str]:
    return {"status": "healthy"}