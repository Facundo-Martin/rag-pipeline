"""Pydantic schemas for the User domain."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Incoming HTTP request payload for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, description="User's plain text password")


class UserRead(BaseModel):
    """Outgoing HTTP response payload for user data."""

    # ConfigDict(from_attributes=True) tells Pydantic to read data
    # directly from your SQLAlchemy ORM model instances.
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
