## Scaffolding project

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

When building a new domain feature (e.g., Users, Billing), build progressively from the database up to the HTTP boundary:

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
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
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
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieves a user by their UUID."""
        pass


class PostgresUserRepository(AbstractUserRepository):
    """
    Concrete SQLAlchemy adapter connecting domain requests to PostgreSQL.
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
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Incoming request payload."""
    email: EmailStr
    password: str


class UserRead(BaseModel):
    """Outgoing response payload."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
```

### 4. Service Layer (Business Logic)

Orchestrate domain rules (e.g., password hashing, uniqueness checks) and repository calls. This layer is completely isolated from HTTP requests and raw SQL.

```python
# src/modules/users/service.py
"""Business use cases and domain workflow orchestration for Users."""

from uuid import UUID

from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate


class UserService:
    """Orchestrates use cases for the User domain."""

    def __init__(self, repo: AbstractUserRepository) -> None:
        """Inject the abstract repository interface."""
        self.repo = repo

    async def register_user(self, data: UserCreate) -> User:
        """Use Case: Register a new unique user."""
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        # In production, hash using Argon2/bcrypt via pwd_context
        user = User(
            email=data.email,
            hashed_password=f"hashed_{data.password}",
        )
        return await self.repo.create(user)

    async def get_user(self, user_id: UUID) -> User | None:
        """Use Case: Fetch a single user by primary key."""
        return await self.repo.get_by_id(user_id)
```

### 5. Lean API Router (HTTP Boundary)

Act strictly as a traffic controller. Parse incoming HTTP requests, inject the necessary services via FastAPI `Depends`, and return proper HTTP status codes.

```python
# src/modules/users/router.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.users.schemas import UserCreate, UserRead
from src.modules.users.service import UserService
from src.modules.users.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Register a new user."""
    try:
        user = await service.register_user(payload)
        return UserRead.model_validate(user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Fetch user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)
```

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

### 6. Unit Testing (Speed & Isolation)

Because the Service layer relies on a Repository interface rather than a hardcoded database connection, we can test complex business logic in milliseconds using in-memory fakes, completely bypassing Docker and Postgres.

```python
# tests/unit/test_user_service.py
"""Unit tests for UserService business logic using an in-memory repository."""

from uuid import UUID, uuid4
import pytest

from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate
from src.modules.users.service import UserService


class FakeUserRepository(AbstractUserRepository):
    """In-memory repository implementing the abstract contract for unit tests."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def create(self, user: User) -> User:
        if not user.id:
            user.id = uuid4()
        self._users[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)


@pytest.mark.anyio
async def test_register_user_success():
    """Verify user registration persists to the repository."""
    repo = FakeUserRepository()
    service = UserService(repo=repo)

    payload = UserCreate(email="test@example.com", password="secretpassword")
    user = await service.register_user(payload)

    assert user.email == "test@example.com"
    persisted_user = await repo.get_by_email("test@example.com")
    assert persisted_user is not None
    assert persisted_user.id == user.id


@pytest.mark.anyio
async def test_register_user_duplicate_email_fails():
    """Verify domain invariance prevents duplicate email registrations."""
    repo = FakeUserRepository()
    service = UserService(repo=repo)

    payload = UserCreate(email="duplicate@example.com", password="secretpassword")
    await service.register_user(payload)

    with pytest.raises(ValueError, match="Email already registered"):
        await service.register_user(payload)
```
