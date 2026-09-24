"""Database repository for Ingestion entities."""

from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ingestion.models import ArxivDocument


class AbstractArxivRepository(ABC):
    """Abstract interface defining data access for ArXiv documents."""

    @abstractmethod
    async def create(self, document: ArxivDocument) -> ArxivDocument:
        """Saves a new document to the data store."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_arxiv_id(self, arxiv_id: str) -> ArxivDocument | None:
        """Retrieves a document by its unique ArXiv ID."""
        raise NotImplementedError


class SqlAlchemyArxivRepository(AbstractArxivRepository):
    """Concrete SQLAlchemy adapter connecting domain requests to Postgres."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, document: ArxivDocument) -> ArxivDocument:
        self._session.add(document)
        await self._session.commit()
        await self._session.refresh(document)
        return document

    async def get_by_arxiv_id(self, arxiv_id: str) -> ArxivDocument | None:
        stmt = select(ArxivDocument).where(ArxivDocument.arxiv_id == arxiv_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
