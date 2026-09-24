"""Base classes and mixins for SQLAlchemy models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, MetaData, Uuid, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Universally recommended SQLAlchemy naming convention for constraints.
# This prevents Alembic migration headaches when dropping/altering columns.
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Root declarative base."""

    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


class IdMixin:
    """
    Standard pattern: Fast internal integer for DB joins,
    secure UUIDv4 for public API exposure.
    """

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    public_id: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        index=True,
        nullable=False,
        server_default=text("gen_random_uuid()"),  # Native PG 13+ UUID generation
    )


class TimestampMixin:
    """Automates created/updated tracking."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
        nullable=False,
    )
