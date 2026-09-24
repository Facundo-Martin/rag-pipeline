"""Database models for the user domain."""

from sqlalchemy import Boolean, CheckConstraint, String, text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base, IdMixin, TimestampMixin


class User(Base, IdMixin, TimestampMixin):
    """SQLAlchemy ORM model for the users table."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email ~ '^[^@]+@[^@]+\\.[^@]+$'", name="email_format"),
        CheckConstraint("LENGTH(hashed_password) > 0", name="password_not_empty"),
        CheckConstraint("created_at <= updated_at", name="timestamps_ordered"),
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
