from fastapi import FastAPI
from src.api.v1.router import api_v1_router

app = FastAPI(title="Modular FastAPI Monolith")

app.include_router(api_v1_router, prefix="/api/v1")