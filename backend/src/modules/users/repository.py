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
