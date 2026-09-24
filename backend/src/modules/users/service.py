"""Business use cases and domain workflow orchestration for Users."""

from uuid import UUID

import structlog
from argon2 import PasswordHasher

from src.modules.users.exceptions import EmailAlreadyExistsError, UserNotFoundError
from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate

logger = structlog.get_logger(__name__)

# Argon2id password hasher (argon2-cffi defaults)
PASSWORD_HASHER = PasswordHasher()


class UserService:
    """Orchestrates use cases for the User domain."""

    def __init__(self, repo: AbstractUserRepository) -> None:
        """Inject the abstract repository interface."""
        self.repo = repo

    async def register_user(self, data: UserCreate) -> User:
        """
        Use Case: Register a new unique user.

        Args:
            data: The validated input data from the HTTP layer.

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

        # 2. Apply business logic (e.g., hash the password)
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
        """Securely hashes a plaintext password using Argon2id."""
        return PASSWORD_HASHER.hash(password)
