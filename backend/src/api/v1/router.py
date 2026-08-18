from fastapi import APIRouter

from src.api.v1.health import health_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
