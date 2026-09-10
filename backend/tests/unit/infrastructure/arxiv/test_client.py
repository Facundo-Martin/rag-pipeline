"""Unit tests for the ArXiv infrastructure adapter."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from src.infrastructure.arxiv.client import ArxivClient, ArxivPaper


@patch("src.infrastructure.arxiv.client.arxiv.Client.results")
def test_fetch_papers_success(mock_results):
    """
    Ensures the adapter correctly maps raw ArXiv results to our DTO schema,
    including cleaning up messy newline characters in titles and summaries.
    """
    # 1. Arrange: Create a mock paper mimicking the raw arxiv.Result object
    mock_paper = MagicMock()
    mock_paper.get_short_id.return_value = "2401.12345v1"
    mock_paper.title = "Agentic RAG\nIs Awesome"
    mock_paper.summary = "This is a summary\nwith newlines."

    mock_author = MagicMock()
    mock_author.name = "Alan Turing"
    mock_paper.authors = [mock_author]

    mock_paper.pdf_url = "https://arxiv.org/pdf/2401.12345v1.pdf"
    mock_paper.published = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    mock_paper.categories = ["cs.AI", "cs.LG"]

    mock_results.return_value = iter([mock_paper])

    client = ArxivClient()

    # 2. Act
    papers = client.fetch_papers(query="Agentic RAG", max_results=1)

    # 3. Assert
    assert len(papers) == 1
    assert isinstance(papers[0], ArxivPaper)
    assert papers[0].entry_id == "2401.12345v1"
    assert papers[0].authors == ["Alan Turing"]
    assert papers[0].title == "Agentic RAG Is Awesome"
    assert papers[0].summary == "This is a summary with newlines."
