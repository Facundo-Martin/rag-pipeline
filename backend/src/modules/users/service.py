"""Business use cases and domain workflow orchestration for Users."""

from uuid import UUID

from src.modules.users.exceptions import EmailAlreadyExistsError
from src.modules.users.models import User
from src.modules.users.repository import AbstractUserRepository
from src.modules.users.schemas import UserCreate


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
            ValueError: If the email is already registered.

        Returns:
            The persisted User domain model.
        """
        # 1. Check invariants (Domain Rule: Email must be unique)
        existing_user = await self.repo.get_by_email(data.email)
        if existing_user:
            raise EmailAlreadyExistsError(f"Email {data.email} is already registered.")

        # 2. Apply business logic (e.g., hash the password)
        hashed_password = self._hash_password(data.password)

        # 3. Create the domain object
        user = User(
            email=data.email,
            hashed_password=hashed_password,
        )

        # 4. Persist via the repository contract
        return await self.repo.create(user)

    async def get_user(self, user_id: UUID) -> User | None:
        """Use Case: Fetch a single user by primary key."""
        return await self.repo.get_by_id(user_id)

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Securely hashes a plaintext password.
        Note: This is a placeholder. Once you build the auth module,
        you will replace this with passlib.context.CryptContext.
        """
        return f"hashed_{password}"
