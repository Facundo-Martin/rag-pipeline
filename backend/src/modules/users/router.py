"""HTTP API endpoints for the User domain."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.modules.users.dependencies import UserServiceDep
from src.modules.users.exceptions import EmailAlreadyExistsError
from src.modules.users.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserServiceDep,
) -> UserRead:
    """
    Register a new user.
    """
    try:
        user = await service.register_user(payload)

        # Pydantic v2 method to convert the SQLAlchemy model into the outgoing schema
        return UserRead.model_validate(user)

    except EmailAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    service: UserServiceDep,
) -> UserRead:
    """
    Fetch a user by their UUID.
    """
    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserRead.model_validate(user)
