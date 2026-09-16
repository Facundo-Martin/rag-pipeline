# pylint: disable=no-member,import-error,invalid-name
import asyncio
import logging

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# 1. Import your app settings
from src.config import get_settings

# 2. Import Base and ALL models so Alembic can see them
from src.infrastructure.postgres.base import Base

# Explicitly import EVERY domain model so SQLAlchemy registers them to Base.metadata
# (Even if your IDE says these are "unused imports", do not remove them!)

# This is the Alembic Config object
config = context.config

# 3. Setup basic logging (Python's fileConfig doesn't support TOML natively)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alembic.env")

# 4. SET THE METADATA (This fixes the autogenerate error!)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    settings = get_settings()

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Synchronous wrapper for the actual migration execution."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode using the async engine."""
    settings = get_settings()

    # Pass the URL directly from your app settings
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
