"""FastAPI dependencies for the ingestion domain."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_db_session
from src.modules.ingestion.repository import AbstractArxivRepository, SqlAlchemyArxivRepository
from src.modules.ingestion.service import IngestionService


def get_arxiv_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AbstractArxivRepository:
    """Injects the concrete SQLAlchemy adapter behind the abstract contract."""
    return SqlAlchemyArxivRepository(session=session)


def get_ingestion_service(
    repo: Annotated[AbstractArxivRepository, Depends(get_arxiv_repository)],
) -> IngestionService:
    """Injects the repository contract into the service layer."""
    return IngestionService(repo=repo)


IngestionServiceDep = Annotated[IngestionService, Depends(get_ingestion_service)]
