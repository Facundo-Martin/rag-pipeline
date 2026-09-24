"""Shared pytest fixtures for database-backed tests."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.infrastructure.postgres.models import Base
from src.infrastructure.postgres.session import get_db_session
from src.main import app

# Setup the Engine using the Pydantic setting (which is now forced to port 5434).
# NullPool avoids reusing connections across the per-test event loops pytest-asyncio creates.
ENGINE = create_async_engine(settings.database_url, poolclass=NullPool)
TESTING_SESSION_LOCAL = async_sessionmaker(
    bind=ENGINE,
    expire_on_commit=False,
    class_=AsyncSession,
    # Let session.commit() hit a savepoint instead of ending the outer transaction,
    # so the fixture can still roll everything back after the test.
    join_transaction_mode="create_savepoint",
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Creates tables once per test run."""
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await ENGINE.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Provides a transactional session for unit/integration tests."""
    async with ENGINE.connect() as conn:
        transaction = await conn.begin()
        async with TESTING_SESSION_LOCAL(bind=conn) as session:
            yield session
        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):  # pylint: disable=redefined-outer-name
    """
    Provides an AsyncClient for FastAPI endpoint testing.
    Overrides the get_db_session dependency to use the isolated fixture.
    """
    # Override the database dependency to use our isolated transaction
    app.dependency_overrides[get_db_session] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up the override after the test
    app.dependency_overrides.clear()
