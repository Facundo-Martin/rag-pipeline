"""Integration tests for the ArXiv Ingestion ETL pipeline."""

import os
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from prefect.testing.utilities import prefect_test_harness
from pydantic import HttpUrl
from sqlalchemy import delete, select

from src.infrastructure.arxiv.schemas import ArxivPaper
from src.infrastructure.docling.schemas import ParsedDocument
from src.infrastructure.postgres.session import get_db_session, init_db
from src.modules.ingestion.models import ArxivDocument
from src.modules.ingestion.workflows import run_etl_pipeline


@pytest.fixture(autouse=True)
def prefect_test_fixture():
    """Runs all Prefect flows in this file against an ephemeral local database."""
    # Disable Prefect telemetry during tests to prevent SQLite locking errors
    os.environ["PREFECT_API_ENABLE_TELEMETRY"] = "0"
    with prefect_test_harness():
        yield


@pytest.fixture
def mock_infrastructure():
    """Mocks the external network and deep learning boundaries."""
    fake_paper = ArxivPaper(
        entry_id="9999.12345v1",
        title="Integration Test Paper",
        summary="A summary for integration testing.",
        authors=["Facundo Martin"],
        pdf_url=HttpUrl("https://arxiv.org/pdf/9999.12345v1"),
        published_date=datetime.now(UTC),
        categories=["cs.AI"],
    )

    fake_parsed = ParsedDocument(
        markdown_content="# Integration Test Markdown Content", char_count=35, elapsed_seconds=0.1
    )

    return fake_paper, fake_parsed


@pytest.mark.anyio
@patch("src.modules.ingestion.workflows.DoclingGateway")
@patch("src.modules.ingestion.workflows.httpx.Client")
@patch("src.modules.ingestion.workflows.ArxivClient")
async def test_run_etl_pipeline_integration(
    mock_arxiv_class, mock_httpx_class, mock_docling_class, mock_infrastructure
):
    """
    Tests the full Prefect flow orchestration, ensuring data passes from the
    infrastructure boundaries all the way into the PostgreSQL database.
    """
    fake_paper, fake_parsed = mock_infrastructure

    # 1. Setup the Mocks
    mock_arxiv_class.return_value.fetch_papers.return_value = [fake_paper]
    mock_docling_class.return_value.parse_pdf.return_value = fake_parsed

    mock_response = MagicMock()
    mock_response.iter_bytes.return_value = [b"fake pdf bytes"]
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_response
    mock_httpx_class.return_value.__enter__.return_value.stream.return_value = mock_context

    # 2. Initialize the Database Connection for Pytest
    test_db_url = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"
    )
    await init_db(test_db_url)

    # --- ACT ---
    await run_etl_pipeline(query="Test Query")

    # --- ASSERT ---
    async for session in get_db_session():
        stmt = select(ArxivDocument).where(ArxivDocument.arxiv_id == "9999.12345v1")
        result = await session.execute(stmt)
        persisted_doc = result.scalar_one_or_none()

        try:
            assert persisted_doc is not None
            assert persisted_doc.title == "Integration Test Paper"
            assert persisted_doc.markdown_content == "# Integration Test Markdown Content"
            assert persisted_doc.embedding_status == "PENDING"
        finally:
            # --- TEARDOWN ---
            if persisted_doc:
                await session.execute(
                    delete(ArxivDocument).where(ArxivDocument.arxiv_id == "9999.12345v1")
                )
                await session.commit()
