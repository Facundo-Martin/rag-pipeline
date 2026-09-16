"""Database models for the ingestion domain."""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.postgres.base import Base, IdMixin, TimestampMixin


class ArxivDocument(Base, IdMixin, TimestampMixin):
    """SQLAlchemy ORM model for storing parsed ArXiv papers."""

    __tablename__ = "arxiv_documents"

    # arxiv_id acts as a natural key alongside the surrogate id/public_id
    arxiv_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)

    authors: Mapped[list[str]] = mapped_column(
        ARRAY(String), server_default=text("'{}'"), nullable=False
    )
    categories: Mapped[list[str]] = mapped_column(
        ARRAY(String), server_default=text("'{}'"), nullable=False
    )

    pdf_url: Mapped[str] = mapped_column(String, nullable=False)
    published_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Track state for the Vectorization ETL Pipeline
    embedding_status: Mapped[str] = mapped_column(
        String(20), server_default=text("'PENDING'"), index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<ArxivDocument {self.arxiv_id}>"
