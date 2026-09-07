"""FastAPI dependencies for the user domain."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Assuming your database session generator is located here based on the scaffolding
from src.infrastructure.postgres.session import get_db_session
from src.modules.users.repository import (
    AbstractUserRepository,
    SqlAlchemyUserRepository,
)
from src.modules.users.service import UserService


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AbstractUserRepository:
    """
    Instantiates the concrete SQLAlchemy adapter but types it as the
    abstract contract. This is the core of Dependency Inversion.
    """
    return SqlAlchemyUserRepository(session=session)


def get_user_service(
    repo: Annotated[AbstractUserRepository, Depends(get_user_repository)],
) -> UserService:
    """Injects the repository contract into the service layer."""
    return UserService(repo=repo)


# Modern FastAPI best practice: Create a type alias for incredibly clean routers
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
