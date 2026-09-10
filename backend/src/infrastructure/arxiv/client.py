"""Infrastructure client for communicating with the external ArXiv API."""

import arxiv
import structlog

from .schemas import ArxivPaper

logger = structlog.get_logger(__name__)


class ArxivClient:
    """
    A wrapper around the ArXiv API to handle rate limits and data extraction.
    """

    def __init__(self):
        """Initializes the client with strict 3-second API rate limits."""
        self.client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)

    def fetch_papers(self, query: str, max_results: int = 10) -> list[ArxivPaper]:
        """
        Executes a search query against ArXiv and parses the results.

        Args:
            query: The keyword search string (e.g., 'Agentic RAG').
            max_results: The maximum number of papers to retrieve.

        Returns:
            A list of validated ArxivPaper Pydantic objects.
        """
        log = logger.bind(query=query, max_results=max_results)
        log.info("arxiv_extraction_started")

        try:
            search = arxiv.Search(query=query, max_results=max_results)
            papers = [
                ArxivPaper(
                    entry_id=p.get_short_id(),
                    title=p.title.replace("\n", " "),
                    summary=p.summary.replace("\n", " "),
                    authors=[a.name for a in p.authors],
                    pdf_url=p.pdf_url,
                    published_date=p.published,
                    categories=p.categories,
                )
                for p in self.client.results(search)
            ]
            log.info("arxiv_extraction_success", count=len(papers))
            return papers
        except Exception as e:
            log.exception("arxiv_extraction_failed", error=str(e))
            raise


if __name__ == "__main__":
    client = ArxivClient()
    results = client.fetch_papers(query="Agentic RAG", max_results=2)
    for idx, paper in enumerate(results):
        print(f"{idx + 1}. {paper.title} ({paper.entry_id})")
