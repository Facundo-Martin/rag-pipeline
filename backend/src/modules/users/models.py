"""Database models for the user domain."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base


class User(Base):
    """
    SQLAlchemy ORM model for the users table.
    Enforces data integrity constraints at the database level.
    """

    # pylint: disable=too-few-public-methods

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email ~ '^[^@]+@[^@]+\\.[^@]+$'", name="ck_email_format"),
        CheckConstraint("LENGTH(hashed_password) > 0", name="ck_password_not_empty"),
        CheckConstraint("created_at <= updated_at", name="ck_timestamps_ordered"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    def __repr__(self) -> str:
        return f"<User {self.email}>"
