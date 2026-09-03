## Scaffolding project

Inspo from: https://oneuptime.com/blog/post/2026-01-26-fastapi-production-ready

Project structure is intiialized with the following one-shot command:

```bash
mkdir -p alembic/versions \
         docker \
         src/api/v1 \
         src/core \
         src/infrastructure/postgres \
         src/infrastructure/qdrant \
         src/infrastructure/redis \
         src/infrastructure/storage \
         src/modules/auth \
         src/modules/users \
         src/modules/billing \
         src/modules/search \
         tests/unit \
         tests/integration && \
touch alembic/env.py \
      alembic/versions/.gitkeep \
      docker/Dockerfile \
      docker/Dockerfile.dev \
      docker/docker-compose.yml \
      src/__init__.py \
      src/main.py \
      src/config.py \
      src/dependencies.py \
      src/api/__init__.py \
      src/api/v1/__init__.py \
      src/api/v1/health.py \
      src/api/v1/router.py \
      src/core/__init__.py \
      src/core/security.py \
      src/core/exceptions.py \
      src/core/middleware.py \
      src/core/rate_limit.py \
      src/infrastructure/__init__.py \
      src/infrastructure/postgres/__init__.py \
      src/infrastructure/postgres/session.py \
      src/infrastructure/postgres/base.py \
      src/infrastructure/qdrant/__init__.py \
      src/infrastructure/qdrant/client.py \
      src/infrastructure/redis/__init__.py \
      src/infrastructure/redis/client.py \
      src/infrastructure/storage/__init__.py \
      src/infrastructure/storage/s3.py \
      src/modules/__init__.py \
      src/modules/auth/__init__.py \
      src/modules/auth/router.py \
      src/modules/auth/schemas.py \
      src/modules/auth/service.py \
      src/modules/users/__init__.py \
      src/modules/users/router.py \
      src/modules/users/schemas.py \
      src/modules/users/models.py \
      src/modules/users/service.py \
      src/modules/users/dependencies.py \
      src/modules/users/exceptions.py \
      src/modules/billing/__init__.py \
      src/modules/billing/router.py \
      src/modules/billing/schemas.py \
      src/modules/billing/models.py \
      src/modules/billing/service.py \
      src/modules/billing/dependencies.py \
      src/modules/search/__init__.py \
      src/modules/search/router.py \
      src/modules/search/schemas.py \
      src/modules/search/service.py \
      tests/__init__.py \
      tests/conftest.py \
      tests/unit/__init__.py \
      tests/integration/__init__.py \
      .env.example \
      .gitignore \
      pyproject.toml \
      README.md && \
cat > docker/Dockerfile <<'EOF'
FROM python:3.12-slim

# Temporary placeholder until the real production image is defined.
EOF
cat > docker/Dockerfile.dev <<'EOF'
FROM python:3.12-slim

# Temporary placeholder until the real dev image is defined.
EOF
```

TODO: This script over-wrote my pyproject.toml file, which it shouldn't have done... fix it
TODO: Rm alembic folders, since these will be created with alembic init

## FastAPI Dev

Our FastAPI entrypoint is specified in pyproject.toml, according to the official [docs](https://fastapi.tiangolo.com/tutorial/first-steps/#configure-the-app-entrypoint-in-pyproject-toml):

```toml
# pyproject.toml

[tool.fastapi]
entrypoint = "src.main:app"
```

Additionally, to simplify development, we are serving it with a Makefile, making it trivial to run the app with `make dev`

```makefile
.PHONY: dev test lint format

dev:
      uv run fastapi dev

test:
      uv run pytest

lint:
      uv run ruff check .

format:
      uv run ruff format .
```

## Docker development

Makefile was updated. Running make dev now spins up docker container for development

## Health and db test

Run make dev and then run either curl -s http://localhost:8000/api/v1/ready or make test, since the db readiness probe has been added to the integration tests

## Data modeling & migrations (later separate into just DB Modeling and DB Migrations)

Refer to "Inverting the Dependency: ORM Depends on Model" section in Chapter 2 of Architecture patterns with Python. However, implementation is done following https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#declarative-mapping, since SQLAlchemy itself recommends it:

> The imperative mapping form is a lesser-used form of mapping that originates from the very first releases of SQLAlchemy in 2006. It’s essentially a means of bypassing the Declarative system to provide a more “barebones” system of mapping, and does not offer modern features such as PEP 484 support. As such, most documentation examples use Declarative forms, and it’s recommended that new users start with Declarative Table configuration.

To push to DB, refer to the makefile

```makefile
# Generate a new migration script (Usage: make db-migrate msg="added users table")
db-migrate:
      uv run alembic -c pyproject.toml revision --autogenerate -m "$(msg)"

# Apply all pending migrations to the database
db-upgrade:
      uv run alembic -c pyproject.toml upgrade head
```

### DB

To verify database tables, you can either use Docker or a Postgres GUI

Docker exec:

```bash
docker exec -it <container_name> psql -U <your_postgres_user> -d <your_db_name>
```

You can find the container name by running `docker ps` and the remaining data in the docker-compose.yml file. The final command is:

```bash
docker exec -it docker-db-1 psql -U postgres -d app_db
```

#### Running on GUI

Based on your docker-compose.yml, your database is exposed perfectly to your host machine on port 5432.

If your GUI tool asks for a Connection URL, you can just paste this exact string: `postgresql://postgres:postgres@localhost:5432/app_db`

## DB Modeling Workflow

We follow the **Dependency Inversion Principle** (inspired by _Architecture Patterns with Python_). High-level business rules must not depend on low-level infrastructure (like FastAPI or SQLAlchemy).
Reference [2: Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository) for further information.

When building a new domain feature (e.g., Users, Billing), build progressively from the database up to the HTTP boundary. Schema here:
https://www.cosmicpython.com/book/images/apwp_0405.png # TODO: Embed image

### 1. ORM Models (Data Structure)

Define the database schema using SQLAlchemy 2.0 Declarative mapping (as recommended by modern SQLAlchemy docs).

```python
# src/modules/users/models.py
"""Database models for the user domain."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base


class User(Base):
    """SQLAlchemy ORM model for the users table."""

    # pylint: disable=too-few-public-methods

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
```

### 2. Repository Pattern (Data Access)

Encapsulate all raw SQL and SQLAlchemy `AsyncSession` operations behind an explicit interface. The rest of the application interacts with the abstract contract, never with the database directly. This enforces strict contracts and makes dependency injection and unit testing predictable.

```python
# src/modules/users/repository.py
"""Database repository for User entities."""

from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.models import User


class AbstractUserRepository(ABC):
    """
    Abstract interface defining data access operations for the User domain.
    Enforces a strict contract for any concrete repository implementation.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Saves a new user to the data store."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieves a user by their UUID."""
        raise NotImplementedError


class SqlAlchemyUserRepository(AbstractUserRepository):
    """
    Concrete SQLAlchemy adapter connecting domain requests to the database.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an async database session."""
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)
```

### 3. Pydantic Schemas (DTOs)

Define strict input/output validation models at the application boundary to sanitize data before it hits business logic.

```python
# src/modules/users/schemas.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Incoming request payload."""

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
    """Outgoing response payload."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### 4. Service Layer (Business Logic)

Orchestrate domain rules (e.g., password hashing, uniqueness checks) and repository calls. This layer is completely isolated from HTTP requests and raw SQL. Raises domain exceptions for error cases instead of returning None.

```python
# src/modules/users/service.py
"""Business use cases and domain workflow orchestration for Users."""

from uuid import UUID

import structlog
from passlib.context import CryptContext

from src.modules.users.exceptions import EmailAlreadyExistsError, UserNotFoundError
from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate

logger = structlog.get_logger(__name__)

# Configure password hashing with argon2 (cryptographically secure)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    """Orchestrates use cases for the User domain."""

    def __init__(self, repo: AbstractUserRepository) -> None:
        """Inject the abstract repository interface."""
        self.repo = repo

    async def register_user(self, data: UserCreate) -> User:
        """
        Use Case: Register a new unique user.

        Raises:
            EmailAlreadyExistsError: If the email is already registered.

        Returns:
            The persisted User domain model.
        """
        logger.info("user_registration_started", email=data.email)

        # 1. Check invariants (Domain Rule: Email must be unique)
        existing_user = await self.repo.get_by_email(data.email)
        if existing_user:
            logger.warning("duplicate_registration_attempt", email=data.email)
            raise EmailAlreadyExistsError(data.email)

        # 2. Apply business logic (hash the password)
        hashed_password = self._hash_password(data.password)

        # 3. Create the domain object
        user = User(
            email=data.email,
            hashed_password=hashed_password,
        )

        # 4. Persist via the repository contract
        created_user = await self.repo.create(user)
        logger.info("user_registration_completed", user_id=str(created_user.id), email=data.email)
        return created_user

    async def get_user(self, user_id: UUID) -> User:
        """
        Use Case: Fetch a single user by primary key.

        Raises:
            UserNotFoundError: If user does not exist.

        Returns:
            The User domain model.
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            logger.warning("user_not_found", user_id=str(user_id))
            raise UserNotFoundError(str(user_id))
        return user

    @staticmethod
    def _hash_password(password: str) -> str:
        """Securely hashes a plaintext password using argon2."""
        return pwd_context.hash(password)
```

### Domain Exceptions (Exception Handling)

Define domain-specific exceptions that extend `AppException`. This enables consistent error handling across the application with proper HTTP status codes.

```python
# src/modules/users/exceptions.py
"""Domain-specific exceptions for the User module."""

from fastapi import status

from src.core.exceptions import AppException


class EmailAlreadyExistsError(AppException):
    """Raised when attempting to register an email that is already in use."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"Email {email} is already registered.",
            status_code=status.HTTP_409_CONFLICT,
        )


class UserNotFoundError(AppException):
    """Raised when a user cannot be found by ID."""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            message=f"User {user_id} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
```

**Key Benefits:**
- Service layer raises domain exceptions (not router handling logic)
- `AppException` handler automatically converts to proper HTTP responses
- Consistent pattern across all modules
- Clear, testable error contracts

### Dependency Injection Wiring (dependencies.py)

To wire the abstract contract into FastAPI's dependency injection container, the dependency provider instantiates the concrete PostgresUserRepository while typing the return value as AbstractUserRepository.

```python
# src/modules/users/dependencies.py

"""FastAPI dependencies for the user domain."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_db_session
from src.modules.users.repository import (
AbstractUserRepository,
PostgresUserRepository,
)
from src.modules.users.service import UserService

def get_user_repository(
session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AbstractUserRepository:
"""Injects the concrete Postgres adapter behind the abstract contract."""
return PostgresUserRepository(session=session)

def get_user_service(
repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
) -> UserService:
"""Injects the repository contract into the service layer."""
return UserService(repo=repo)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

### 5. Lean API Router (HTTP Boundary)

Act strictly as a traffic controller. Parse incoming HTTP requests, inject the necessary services via FastAPI `Depends`, and return proper HTTP status codes. Service exceptions bubble up and are automatically handled by the `AppException` handler.

```python
# src/modules/users/router.py
"""HTTP API endpoints for the User domain."""

from uuid import UUID

from fastapi import APIRouter, status

from src.modules.users.dependencies import UserServiceDep
from src.modules.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserServiceDep,
) -> UserRead:
    """
    Register a new user.

    Returns a 201 Created with the user details.

    Raises:
        EmailAlreadyExistsError: If email is already registered (409 Conflict).
        ValidationError: If email or password doesn't meet requirements (422).
    """
    user = await service.register_user(payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    service: UserServiceDep,
) -> UserRead:
    """
    Fetch a user by their UUID.

    Returns 200 with user details or 404 if not found.

    Raises:
        UserNotFoundError: If user does not exist (404 Not Found).
    """
    user = await service.get_user(user_id)
    return UserRead.model_validate(user)
```

**Key Observations:**
- No try/except blocks - exceptions bubble to `AppException` handler
- No manual `HTTPException` creation - domain exceptions handle it
- Service is injected via `UserServiceDep` type alias (clean FastAPI pattern)
- Router is minimal and focused - just HTTP marshaling

### 6. Unit Testing (Speed & Isolation)

Because the Service layer relies on a Repository interface rather than a hardcoded database connection, we can test complex business logic in milliseconds using in-memory fakes, completely bypassing Docker and Postgres.

```python
# tests/unit/test_user_service.py
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
        # Simulate database assigning an ID and timestamps if missing
        if not user.id:
            user.id = uuid4()
        if not getattr(user, "created_at", None):
            user.created_at = datetime.now(UTC)
        if not getattr(user, "updated_at", None):
            user.updated_at = datetime.now(UTC)

        self._users[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)


@pytest.mark.anyio
async def test_register_user_success():
    """Verify user registration persists to the repository with secure hashing."""
    repo = FakeUserRepository()
    service = UserService(repo=repo)

    payload = UserCreate(email="test@example.com", password="SecurePass123")
    user = await service.register_user(payload)

    assert user.email == "test@example.com"

    # Verify it was actually saved in our fake repo
    persisted_user = await repo.get_by_email("test@example.com")
    assert persisted_user is not None
    assert persisted_user.id == user.id
    # Ensure password was hashed (argon2 hash is different each time)
    assert persisted_user.hashed_password != "SecurePass123"
    assert persisted_user.hashed_password.startswith("$argon2")


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
```

### 7. Integration Testing (End-to-End)

Test the full stack from HTTP boundary through service layer to database with dependency injection overrides.

```python
# tests/integration/test_users_api.py
"""End-to-End API tests for the Users domain."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.modules.users.dependencies import get_user_repository
from tests.unit.test_user_service import FakeUserRepository


@pytest.fixture
def override_user_repository():
    """Overrides the FastAPI dependency injection to use our in-memory fake repo."""
    fake_repo = FakeUserRepository()
    app.dependency_overrides[get_user_repository] = lambda: fake_repo
    yield fake_repo
    app.dependency_overrides.clear()


@pytest.mark.anyio
@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_e2e():
    """Test the full request/response cycle without hitting Postgres."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={"email": "e2e@example.com", "password": "SecurePass123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "e2e@example.com"
        assert "id" in data
        assert data["is_active"] is True


@pytest.mark.anyio
@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_duplicate_email_returns_409():
    """Test that duplicate emails return 409 Conflict with proper error message."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create first user
        response1 = await client.post(
            "/api/v1/users",
            json={"email": "duplicate@example.com", "password": "FirstPass123"},
        )
        assert response1.status_code == 201

        # Try to register with same email
        response2 = await client.post(
            "/api/v1/users",
            json={"email": "duplicate@example.com", "password": "SecondPass456"},
        )

        assert response2.status_code == 409
        data = response2.json()
        assert "error" in data
        assert "already registered" in data["error"]["message"]


@pytest.mark.anyio
@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_weak_password_returns_422():
    """Test that weak passwords are rejected during validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={"email": "weak@example.com", "password": "weakpass123"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


@pytest.mark.anyio
@pytest.mark.usefixtures("override_user_repository")
async def test_get_user_not_found_returns_404():
    """Test that fetching a non-existent user returns 404."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        nonexistent_id = uuid4()
        response = await client.get(f"/api/v1/users/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"]["message"]
```

## Best Practices Implemented

### Password Security
- **Argon2 hashing**: Industry-standard memory-hard hashing algorithm (resistant to GPU/ASIC attacks)
- **Password validation**: Enforced at Pydantic level (uppercase, lowercase, digit, 8-128 chars)
- **No plaintext storage**: Passwords are hashed before database persistence

### Exception Handling Pattern
- **Domain exceptions** (EmailAlreadyExistsError, UserNotFoundError) extend `AppException`
- **Automatic HTTP mapping**: AppException handler converts domain exceptions to proper HTTP status codes
- **Consistent across modules**: Same pattern for billing, search, auth modules
- **No business logic in routers**: Service layer raises exceptions, router lets them bubble up

### Structured Logging
- **Observability**: Service layer logs significant events with context
  - `user_registration_started` - tracks registration flow
  - `duplicate_registration_attempt` - tracks failed attempts
  - `user_registration_completed` - tracks successful completions
  - `user_not_found` - tracks lookup failures
- **Integration with structlog**: Automatically formatted for development (pretty) and production (JSON)
- **Correlation context**: Request IDs and other context automatically propagated

### Testing Strategy
- **Unit tests fast**: 0.58s for service logic using in-memory fakes
- **Integration tests comprehensive**: End-to-end tests prove error handling works
- **Test both happy paths and errors**: Success, duplicates, validation failures, not found
- **No database in unit tests**: Clean isolation with repository abstraction
- **Dependency override pattern**: Integration tests inject fake repositories without mocking

### Clean Architecture
- **Repository Pattern**: Abstract data access, enable multiple implementations
- **Dependency Inversion**: Service depends on interfaces, not concrete implementations
- **Layered separation**: HTTP → Service → Repository → Database
- **Single responsibility**: Each layer has one reason to change
