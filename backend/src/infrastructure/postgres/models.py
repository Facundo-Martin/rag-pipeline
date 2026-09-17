"""
Central model registry.

SQLAlchemy declarative models self-register on ``Base.metadata`` at import time,
so every slice's models must be imported before Alembic autogenerate or
``Base.metadata.create_all()`` can see them. Import this module (or ``Base``
from it) wherever the full schema is needed: Alembic config, tests, etc.
"""

# pylint: disable=unused-import

from src.infrastructure.postgres.base import Base
from src.modules import ingestion, users  # noqa: F401

__all__ = ["Base"]
