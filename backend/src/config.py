from enum import Enum
from functools import lru_cache
from typing import Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """
    Runtime environment options.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Use .env file for local development.
    """

    # Application settings
    app_name: str = Field(
        default="Modular FastAPI Backend",
        description="Display name of the application in API documentation.",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode for verbose error logging and API docs.",
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Runtime environment mode.",
    )
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="Global route prefix for V1 endpoints.",
    )

    # Server settings
    host: str = Field(
        default="0.0.0.0",
        description="Host address to bind the server.",
    )
    port: int = Field(
        default=8000,
        description="Port number to bind the server.",
    )
    workers: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker processes for production ASGI deployments.",
    )

    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/app_db",
        description="Async SQLAlchemy connection URL for the PostgreSQL database.",
    )
    db_pool_size: int = Field(
        default=10,
        description="Number of database connections maintained in the pool.",
    )
    db_max_overflow: int = Field(
        default=20,
        description="Maximum temporary database connections allowed beyond the pool size.",
    )

    # Security settings
    secret_key: SecretStr = Field(
        default=SecretStr("insecure-dev-secret-key-change-me-in-production-32-chars"),
        min_length=32,
        description="Secret key for JWT generation and cryptographic operations.",
    )

    # CORS settings
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for cross-origin resource sharing.",
    )

    # Load from .env file if present and ignore extra local variables.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def set_debug_default(self) -> Self:
        """
        Default debug to True for non-production environments unless explicitly set.
        """
        if "debug" not in self.model_fields_set:
            self.debug = self.environment != Environment.PRODUCTION
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache ensures settings are loaded once.
    """
    return Settings()


settings = get_settings()
