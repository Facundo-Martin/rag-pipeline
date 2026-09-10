"""Business use cases and domain workflow orchestration for Ingestion."""

import structlog

from src.infrastructure.arxiv.schemas import ArxivPaper
from src.infrastructure.docling.schemas import ParsedDocument
from src.modules.ingestion.exceptions import DocumentAlreadyExistsError
from src.modules.ingestion.models import ArxivDocument
from src.modules.ingestion.repository import AbstractArxivRepository

logger = structlog.get_logger(__name__)


class IngestionService:
    """Orchestrates use cases for the Ingestion domain."""

    def __init__(self, repo: AbstractArxivRepository) -> None:
        """Inject the abstract repository interface."""
        self.repo = repo

    async def load_document(self, paper: ArxivPaper, parsed_doc: ParsedDocument) -> ArxivDocument:
        """
        Use Case: Persist the extracted metadata and parsing results.

        Raises:
            DocumentAlreadyExistsError: If the paper is already in the database.

        Returns:
            The persisted ArxivDocument domain model.
        """
        logger.info("ingestion_load_started", arxiv_id=paper.entry_id)

        # 1. Check invariants (Domain Rule: ArXiv IDs must be unique)
        existing_doc = await self.repo.get_by_arxiv_id(paper.entry_id)
        if existing_doc:
            logger.warning("duplicate_ingestion_attempt", arxiv_id=paper.entry_id)
            raise DocumentAlreadyExistsError(paper.entry_id)

        # 2. Create the domain object from our DTOs
        new_doc = ArxivDocument(
            arxiv_id=paper.entry_id,
            title=paper.title,
            summary=paper.summary,
            markdown_content=parsed_doc.markdown_content,
            authors=paper.authors,
            categories=paper.categories,
            pdf_url=str(paper.pdf_url),
            published_date=paper.published_date,
        )

        # 3. Persist via the repository contract
        created_doc = await self.repo.create(new_doc)

        logger.info(
            "ingestion_load_completed", internal_id=str(created_doc.id), arxiv_id=paper.entry_id
        )
        return created_doc
