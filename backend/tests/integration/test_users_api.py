"""End-to-End API tests for the Users domain."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.modules.users.dependencies import get_user_repository
from tests.unit.test_user_service import FakeUserRepository


@pytest.fixture
def override_user_repository():
    """Overrides the FastAPI dependency injection to use our in-memory fake repo."""
    fake_repo = FakeUserRepository()
    app.dependency_overrides[get_user_repository] = lambda: fake_repo
    yield fake_repo
    app.dependency_overrides.clear()


@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_e2e():
    """Test the API Router and Service layer without hitting Postgres."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={"email": "e2e@example.com", "password": "SecurePass123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "e2e@example.com"
        assert "id" in data
        assert data["is_active"] is True


@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_duplicate_email_returns_409():
    """Test that duplicate emails return 409 Conflict with proper error message."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create first user
        response1 = await client.post(
            "/api/v1/users",
            json={"email": "duplicate@example.com", "password": "FirstPass123"},
        )
        assert response1.status_code == 201

        # Try to register with same email
        response2 = await client.post(
            "/api/v1/users",
            json={"email": "duplicate@example.com", "password": "SecondPass456"},
        )

        assert response2.status_code == 409
        data = response2.json()
        assert "error" in data
        assert "already registered" in data["error"]["message"]


@pytest.mark.usefixtures("override_user_repository")
async def test_create_user_weak_password_returns_422():
    """Test that weak passwords are rejected during validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing uppercase letter
        response = await client.post(
            "/api/v1/users",
            json={"email": "weak@example.com", "password": "weakpass123"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data


@pytest.mark.usefixtures("override_user_repository")
async def test_get_user_not_found_returns_404():
    """Test that fetching a non-existent user returns 404."""
    from uuid import uuid4

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        nonexistent_id = uuid4()
        response = await client.get(f"/api/v1/users/{nonexistent_id}")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "not found" in data["error"]["message"]
