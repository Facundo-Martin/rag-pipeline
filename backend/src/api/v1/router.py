from fastapi import APIRouter

from src.api.v1.health import health_router
from src.modules.users.router import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])

api_v1_router.include_router(users_router)
