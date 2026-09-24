"""Pydantic schemas for the User domain."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Incoming HTTP request payload for user registration."""

    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password must be 8-128 chars with uppercase, lowercase, and digit",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password contains uppercase, lowercase, and digit."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(BaseModel):
    """Outgoing HTTP response payload for user data."""

    # ConfigDict(from_attributes=True) tells Pydantic to read data
    # directly from your SQLAlchemy ORM model instances.
    model_config = ConfigDict(from_attributes=True)

    # Expose the public UUID (public_id) to clients; the integer `id`
    # is an internal surrogate key only.
    id: UUID = Field(validation_alias="public_id")
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
