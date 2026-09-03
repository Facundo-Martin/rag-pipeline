"""Unit tests for UserService business logic using an in-memory repository."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.modules.users.exceptions import EmailAlreadyExistsError
from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate
from src.modules.users.service import UserService


class FakeUserRepository(AbstractUserRepository):
    """In-memory repository implementing the abstract contract for unit tests."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def create(self, user: User) -> User:
        # Simulate database assigning an ID and created_at timestamps if missing
        if not user.id:
            user.id = uuid4()

        # Simulate PostgreSQL generating default values
        if getattr(user, "is_active", None) is None:
            user.is_active = True
        if not getattr(user, "created_at", None):
            user.created_at = datetime.now(UTC)
        if not getattr(user, "updated_at", None):
            user.updated_at = datetime.now(UTC)

        self._users[user.id] = user
        return user

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)


@pytest.mark.anyio
async def test_register_user_success():
    """Verify user registration persists to the repository."""
    repo = FakeUserRepository()
    service = UserService(repo=repo)

    payload = UserCreate(email="test@example.com", password="SecurePass123")
    user = await service.register_user(payload)

    assert user.email == "test@example.com"

    # Verify it was actually saved in our fake repo
    persisted_user = await repo.get_by_email("test@example.com")
    assert persisted_user is not None
    assert persisted_user.id == user.id
    # Ensure password was hashed (argon2 hash is different each time, so just check it's not plaintext)
    assert persisted_user.hashed_password != "SecurePass123"
    assert persisted_user.hashed_password.startswith("$argon2")  # argon2 hash format


@pytest.mark.anyio
async def test_register_user_duplicate_email_fails():
    """Verify domain invariance prevents duplicate email registrations."""
    repo = FakeUserRepository()
    service = UserService(repo=repo)

    payload = UserCreate(email="duplicate@example.com", password="SecurePass123")

    # First registration succeeds
    await service.register_user(payload)

    # Second registration with same email should raise EmailAlreadyExistsError
    with pytest.raises(EmailAlreadyExistsError, match="is already registered"):
        await service.register_user(payload)
