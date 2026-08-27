import logging
from typing import Any, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
    """
    # Tell Mypy to treat this as a RequestValidationError
    exc = cast(RequestValidationError, exc)

    logger.info("Validation error on path=%s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "details": exc.errors(),
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
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
