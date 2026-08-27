"""Manage the asynchronous PostgreSQL engine and request-scoped sessions."""

from collections.abc import AsyncGenerator
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config import get_settings

# SQLAlchemy base class for models
Base = declarative_base()


@dataclass
class _DatabaseState:
    """Hold the database resources shared by the application process."""

    engine: AsyncEngine | None = None
    session_factory: async_sessionmaker[AsyncSession] | None = None


_DATABASE_STATE = _DatabaseState()


async def init_db(database_url: str) -> None:
    """
    Initialize database engine and session factory.
    Call this during application startup.
    """
    settings = get_settings()

    # Create async engine with connection pooling
    _DATABASE_STATE.engine = create_async_engine(
        str(database_url),
        echo=settings.debug,  # Log SQL in debug mode
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Create session factory
    _DATABASE_STATE.session_factory = async_sessionmaker(
        bind=_DATABASE_STATE.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def close_db() -> None:
    """
    Close database connections.
    Call this during application shutdown.
    """
    if _DATABASE_STATE.engine:
        await _DATABASE_STATE.engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency that provides a database session.
    Session is automatically closed after the request.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    session_factory = _DATABASE_STATE.session_factory
    if session_factory is None:
        raise RuntimeError("Database not initialized")

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
