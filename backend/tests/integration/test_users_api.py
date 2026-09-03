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


@pytest.mark.anyio
@pytest.mark.usefixtures("override_user_repository")  # <-- ADD THIS DECORATOR
async def test_create_user_e2e():
    """Test the API Router and Service layer without hitting Postgres."""

    # Notice we removed the argument from the function signature above!
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/users",
            json={"email": "e2e@example.com", "password": "secure1234"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "e2e@example.com"
