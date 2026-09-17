import logging
from typing import Any, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Base exception class for custom domain and application errors.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class BadRequestException(AppException):
    """
    Raised when the client sends an invalid request payload or parameters.
    """

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class UnauthorizedException(AppException):
    """
    Raised when authentication credentials are missing or invalid.
    """

    def __init__(
        self,
        message: str = "Unauthorized access",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenException(AppException):
    """
    Raised when an authenticated user lacks permission to perform an action.
    """

    def __init__(
        self,
        message: str = "Access forbidden",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class NotFoundException(AppException):
    """
    Raised when a requested database record or resource is missing.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for structured application exceptions.
    """
    # Tell Mypy to treat this as an AppException
    exc = cast(AppException, exc)

    logger.warning(
        "Domain exception occurred: path=%s status=%d message='%s'",
        request.url.path,
        exc.status_code,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for Pydantic request validation errors.
    Serializes errors in a clean, JSON-safe format.
    """
    # Tell Mypy to treat this as a RequestValidationError
    exc = cast(RequestValidationError, exc)

    errors = exc.errors()
    logger.info("Validation error on path=%s: %s", request.url.path, errors)

    # Clean up errors to ensure JSON serializability
    # Remove context objects that can't be serialized
    cleaned_errors = []
    for error in errors:
        clean_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
        }
        cleaned_errors.append(clean_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "message": "Validation error",
                "details": cleaned_errors,
            }
        },
    )


async def integrity_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for SQLAlchemy IntegrityError (database constraint violations).
    Maps database constraint violations to appropriate HTTP status codes.
    """
    exc = cast(IntegrityError, exc)

    # Extract constraint name from error message
    error_message = str(exc.orig)
    constraint = getattr(exc, "constraint", None)
    constraint_name = str(constraint) if constraint else ""

    # Map specific constraint violations to appropriate messages
    if "unique" in error_message.lower() or (constraint_name and "uq" in constraint_name.lower()):
        status_code = status.HTTP_409_CONFLICT
        message = "Resource already exists"
    elif "check" in error_message.lower() or (constraint_name and "ck" in constraint_name.lower()):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        message = "Constraint validation failed"
    elif "foreign key" in error_message.lower():
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        message = "Invalid reference to related resource"
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Database constraint violation"

    logger.warning(
        "Database integrity violation: path=%s constraint=%s error=%s",
        request.url.path,
        constraint_name,
        error_message,
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "details": {"constraint": constraint_name} if constraint_name else {},
            }
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled internal exceptions.
    Logs the full traceback for debugging without exposing internal details to the client.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected internal server error occurred.",
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with the FastAPI application instance.
    Order matters: more specific exceptions should be registered before general ones.
    """
    # Domain exceptions (most specific)
    app.add_exception_handler(AppException, app_exception_handler)
    # Database constraint violations
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # Catch-all (least specific)
    app.add_exception_handler(Exception, unhandled_exception_handler)
