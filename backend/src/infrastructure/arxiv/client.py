"""Infrastructure client for communicating with the external ArXiv API."""

import arxiv  # type: ignore[import-untyped]
import structlog
from pydantic import HttpUrl

from .schemas import ArxivPaper

# Initialize structlog to automatically pick up the config defined in your main setup
logger = structlog.get_logger(__name__)


class ArxivClientError(Exception):
    """Base exception for ArXiv client network or parsing errors."""


class ArxivClient:
    """
    A wrapper around the ArXiv API to handle rate limits, network retries,
    and strict data extraction into domain DTOs.
    """

    def __init__(self, delay_seconds: float = 3.0, num_retries: int = 3):
        """
        Initializes the ArXiv client configuration.

        Args:
            delay_seconds: Crucial for respecting ArXiv's rate limits (API docs mandate ~3s).
            num_retries: Automatic retries for network drops.
        """
        self.delay_seconds = delay_seconds
        self.num_retries = num_retries
        logger.debug(
            "arxiv_client_config_initialized",
            delay_seconds=delay_seconds,
            num_retries=num_retries,
        )

    def fetch_papers(self, query: str, max_results: int = 1) -> list[ArxivPaper]:
        """
        Executes a search query against ArXiv and parses the results.

        Args:
            query: The keyword search string (e.g., 'Agentic RAG').
            max_results: The maximum number of papers to retrieve.

        Returns:
            A list of validated ArxivPaper Pydantic objects.

        Raises:
            ArxivClientError: If the API rejects the request or network fails.
        """
        log = logger.bind(query=query, max_results=max_results)
        log.info("fetching_arxiv_papers_started")

        # CRITICAL FIX: Instantiate the client dynamically per request.
        # Matching page_size to max_results prevents triggering 429 limits with massive batches.
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=self.delay_seconds,
            num_retries=self.num_retries,
        )

        try:
            search = arxiv.Search(
                query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
            )

            raw_results = list(client.results(search))
            papers: list[ArxivPaper] = []

            for p in raw_results:
                if p.pdf_url is None:
                    raise ArxivClientError(
                        f"ArXiv returned no PDF URL for paper {p.get_short_id()}"
                    )

                papers.append(
                    ArxivPaper(
                        entry_id=p.get_short_id(),
                        # Clean up ArXiv's messy newline characters in text fields
                        title=p.title.replace("\n", " "),
                        summary=p.summary.replace("\n", " "),
                        authors=[a.name for a in p.authors],
                        pdf_url=HttpUrl(p.pdf_url),
                        published_date=p.published,
                        categories=p.categories,
                    )
                )

            log.info("fetching_arxiv_papers_success", count=len(papers))
            return papers

        except arxiv.ArxivError as e:
            # Catch library-specific errors and wrap them in our domain exception
            log.error("arxiv_api_error", error=str(e))
            raise ArxivClientError(f"ArXiv API rejected the request: {e!s}") from e
        except Exception as e:
            # Catch general network/timeout errors
            log.exception("arxiv_network_or_parsing_error", error=str(e))
            raise ArxivClientError(f"Failed to fetch papers from ArXiv: {e!s}") from e


# Note: Test with uv run python -m src.infrastructure.arxiv.client
if __name__ == "__main__":
    # Local execution test
    test_client = ArxivClient()
    results = test_client.fetch_papers(query="Agentic RAG", max_results=2)
    for idx, paper in enumerate(results):
        print(f"{idx + 1}. {paper.title} ({paper.entry_id})")
