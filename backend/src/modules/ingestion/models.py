"""Database models for the ingestion domain."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base


class ArxivDocument(Base):
    """SQLAlchemy ORM model for storing parsed ArXiv papers."""

    __tablename__ = "arxiv_documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    arxiv_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)

    authors: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    pdf_url: Mapped[str] = mapped_column(String, nullable=False)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ArxivDocument {self.arxiv_id}>"
