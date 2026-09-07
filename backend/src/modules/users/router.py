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
