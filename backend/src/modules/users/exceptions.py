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
