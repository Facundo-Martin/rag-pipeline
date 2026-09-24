"""Prefect orchestration workflow acting as a Driving Adapter."""

import asyncio
import tempfile
from pathlib import Path

import httpx
from prefect import flow, task
from prefect.logging import get_run_logger

from src.infrastructure.arxiv.client import ArxivClient
from src.infrastructure.arxiv.schemas import ArxivPaper
from src.infrastructure.docling.parser import DoclingGateway
from src.infrastructure.docling.schemas import ParsedDocument
from src.infrastructure.postgres.session import get_db_session
from src.modules.ingestion.exceptions import DocumentAlreadyExistsError
from src.modules.ingestion.repository import SqlAlchemyArxivRepository
from src.modules.ingestion.service import IngestionService


@task(retries=2, retry_delay_seconds=5)
def extract_metadata_task(query: str) -> list[ArxivPaper]:
    """Fetches the latest paper metadata from the ArXiv API using a keyword search."""
    logger = get_run_logger()
    logger.info("Fetching ArXiv metadata for query: '%s'", query)

    client = ArxivClient()
    papers = client.fetch_papers(query=query, max_results=1)

    if not papers:
        logger.error("No papers found for query: '%s'. Aborting pipeline.", query)
        raise ValueError(f"No papers found for query: {query}")

    logger.info("Successfully extracted metadata for ArXiv ID: %s", papers[0].entry_id)
    return papers


@task(retries=3, retry_delay_seconds=5)
def download_pdf_task(url: str) -> str:
    """Downloads a PDF from a given URL to a temporary local file."""
    logger = get_run_logger()
    logger.info("Starting PDF download from: %s", url)

    with (
        tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp,
        httpx.Client(follow_redirects=True) as client,
        client.stream("GET", url) as response,
    ):
        response.raise_for_status()

        for chunk in response.iter_bytes(chunk_size=8192):
            tmp.write(chunk)

        logger.info("PDF downloaded successfully to temporary path: %s", tmp.name)
        return tmp.name


@task
def parse_pdf_task(pdf_path: str) -> ParsedDocument:
    """Processes a local PDF file through Docling's vision models to extract Markdown."""
    logger = get_run_logger()
    logger.info("Initializing Docling parser for file: %s", pdf_path)

    gateway = DoclingGateway(enable_ocr=False)
    parsed_doc = gateway.parse_pdf(pdf_path)

    logger.info(
        "Parsing complete. Extracted %d characters in %.2f seconds.",
        parsed_doc.char_count,
        parsed_doc.elapsed_seconds,
    )
    return parsed_doc


@task(retries=2, retry_delay_seconds=5)
async def load_to_database_task(paper: ArxivPaper, parsed_doc: ParsedDocument) -> bool:
    """
    Persists the extracted metadata and markdown content into the PostgreSQL database.
    Returns True if successfully inserted, False if skipped (already exists).
    """
    logger = get_run_logger()
    logger.info("Attempting to load ArXiv ID %s into database.", paper.entry_id)

    async for session in get_db_session():
        repo = SqlAlchemyArxivRepository(session=session)
        service = IngestionService(repo=repo)

        try:
            await service.load_document(paper=paper, parsed_doc=parsed_doc)
            logger.info("Successfully persisted ArXiv ID %s to database.", paper.entry_id)
            return True

        except DocumentAlreadyExistsError:
            logger.warning(
                "Document %s already exists in the database. Skipping insertion.", paper.entry_id
            )
            return False
        except Exception as e:
            logger.error("Database insertion failed for ArXiv ID %s: %s", paper.entry_id, str(e))
            raise

    raise RuntimeError("No database session available to persist document.")


@flow(name="ArXiv ETL Pipeline", log_prints=True)
async def run_etl_pipeline(query: str = "Agentic RAG"):
    """
    Coordinates the extraction of ArXiv metadata, downloading of PDFs,
    ML-driven text extraction, and database persistence.
    """
    logger = get_run_logger()
    logger.info("Starting ETL Pipeline run for query: '%s'", query)

    # 1. Extract
    papers = extract_metadata_task(query=query)
    paper = papers[0]

    # 2. Download
    pdf_path = download_pdf_task(url=str(paper.pdf_url))

    try:
        # 3. Transform
        parsed_doc = parse_pdf_task(pdf_path=pdf_path)

        # 4. Load
        inserted = await load_to_database_task(paper=paper, parsed_doc=parsed_doc)

        if inserted:
            logger.info(
                "🎉 Pipeline completed successfully. New document ingested: %s", paper.entry_id
            )
        else:
            logger.info(
                "✅ Pipeline completed. Document was already up to date: %s", paper.entry_id
            )

    finally:
        # 5. Cleanup
        path_obj = Path(pdf_path)
        if path_obj.exists():
            path_obj.unlink()
            logger.debug("Cleaned up temporary file: %s", pdf_path)


if __name__ == "__main__":
    import os

    from src.infrastructure.postgres.session import init_db

    async def run_local_test():
        """Bootstraps the local DB connection and runs the flow."""
        # Use localhost since we are running outside the Docker network
        if "DATABASE_URL" not in os.environ:
            os.environ["DATABASE_URL"] = (
                "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"
            )

        # Await the async database initialization
        await init_db(os.environ["DATABASE_URL"])

        # Execute the pipeline
        await run_etl_pipeline()

    # Run the wrapper
    asyncio.run(run_local_test())
