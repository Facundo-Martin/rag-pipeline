"""Pydantic schemas for validating and structuring ArXiv data."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ArxivPaper(BaseModel):
    """
    Represents the core metadata of an ArXiv paper.

    Used as the standard data contract for passing ArXiv
    results across system boundaries.
    """

    entry_id: str = Field(..., description="Unique ArXiv identifier")
    title: str
    summary: str
    authors: list[str] = Field(default_factory=list)
    pdf_url: HttpUrl
    published_date: datetime
    categories: list[str] = Field(default_factory=list)
