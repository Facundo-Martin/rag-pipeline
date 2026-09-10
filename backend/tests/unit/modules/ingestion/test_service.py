"""Unit tests for IngestionService business logic using an in-memory repository."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.infrastructure.arxiv.schemas import ArxivPaper
from src.infrastructure.docling.schemas import ParsedDocument
from src.modules.ingestion.exceptions import DocumentAlreadyExistsError
from src.modules.ingestion.models import ArxivDocument
from src.modules.ingestion.repository import AbstractArxivRepository
from src.modules.ingestion.service import IngestionService


class FakeArxivRepository(AbstractArxivRepository):
    """In-memory repository implementing the abstract contract for unit tests."""

    def __init__(self) -> None:
        self._docs: dict[str, ArxivDocument] = {}

    async def create(self, document: ArxivDocument) -> ArxivDocument:
        if not document.id:
            document.id = uuid4()
        if not getattr(document, "created_at", None):
            document.created_at = datetime.now(UTC)
        if not getattr(document, "updated_at", None):
            document.updated_at = datetime.now(UTC)

        self._docs[document.arxiv_id] = document
        return document

    async def get_by_arxiv_id(self, arxiv_id: str) -> ArxivDocument | None:
        return self._docs.get(arxiv_id)


@pytest.fixture
def sample_dtos():
    paper = ArxivPaper(
        entry_id="2405.12345v1",
        title="Test Paper",
        summary="A summary",
        authors=["Alice", "Bob"],
        pdf_url="https://arxiv.org/pdf/2405.12345v1",
        published_date=datetime(2026, 1, 1, tzinfo=UTC),
        categories=["cs.AI"],
    )
    parsed = ParsedDocument(markdown_content="# Test Content", char_count=14, elapsed_seconds=1.5)
    return paper, parsed


@pytest.mark.anyio
async def test_load_document_success(sample_dtos):
    """Verify document load persists to the repository."""
    paper, parsed = sample_dtos
    repo = FakeArxivRepository()
    service = IngestionService(repo=repo)

    doc = await service.load_document(paper, parsed)

    assert doc.arxiv_id == "2405.12345v1"
    assert doc.markdown_content == "# Test Content"

    # Verify it was actually saved in our fake repo
    persisted_doc = await repo.get_by_arxiv_id("2405.12345v1")
    assert persisted_doc is not None
    assert persisted_doc.id == doc.id


@pytest.mark.anyio
async def test_load_document_duplicate_fails(sample_dtos):
    """Verify domain invariance prevents duplicate document ingestion."""
    paper, parsed = sample_dtos
    repo = FakeArxivRepository()
    service = IngestionService(repo=repo)

    # First load succeeds
    await service.load_document(paper, parsed)

    # Second load with same arxiv_id should raise DocumentAlreadyExistsError
    with pytest.raises(DocumentAlreadyExistsError, match="already ingested"):
        await service.load_document(paper, parsed)
