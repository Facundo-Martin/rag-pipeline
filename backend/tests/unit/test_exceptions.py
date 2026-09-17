import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    register_exception_handlers,
)


@pytest.fixture
def test_app() -> FastAPI:
    """
    Creates a lightweight FastAPI app with dummy endpoints
    to test custom exception handling logic in isolation.
    """
    app = FastAPI()

    @app.get("/test-400")
    async def route_400():
        raise BadRequestException(
            message="Invalid parameter provided",
            details={"field": "query_param"},
        )

    @app.get("/test-401")
    async def route_401():
        raise UnauthorizedException(message="Token expired")

    @app.get("/test-403")
    async def route_403():
        raise ForbiddenException(message="Insufficient permissions")

    @app.get("/test-404")
    async def route_404():
        raise NotFoundException(message="User record not found")

    @app.get("/test-500")
    async def route_500():
        raise RuntimeError("Database connection pool exhausted")

    register_exception_handlers(app)
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    # raise_server_exceptions=False prevents TestClient from re-raising 500s during tests
    return TestClient(test_app, raise_server_exceptions=False)


def test_bad_request_exception(client: TestClient):
    response = client.get("/test-400")
    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "message": "Invalid parameter provided",
            "details": {"field": "query_param"},
        }
    }


def test_unauthorized_exception(client: TestClient):
    response = client.get("/test-401")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "message": "Token expired",
            "details": {},
        }
    }


def test_forbidden_exception(client: TestClient):
    response = client.get("/test-403")
    assert response.status_code == 403
    assert response.json() == {
        "error": {
            "message": "Insufficient permissions",
            "details": {},
        }
    }


def test_not_found_exception(client: TestClient):
    response = client.get("/test-404")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "message": "User record not found",
            "details": {},
        }
    }


def test_unhandled_exception_masking(client: TestClient, caplog: pytest.LogCaptureFixture):
    """Internal errors are masked in the response while the traceback is logged server-side."""
    # The catch-all handler intentionally logs the full traceback; suppress that
    # expected error output so it does not pollute the test run.
    with caplog.at_level(logging.CRITICAL, logger="src.core.exceptions"):
        response = client.get("/test-500")
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "message": "An unexpected internal server error occurred.",
        }
    }
