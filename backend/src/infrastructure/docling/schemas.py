"""Pydantic schemas (DTOs) for the Docling parsing gateway."""

from pydantic import BaseModel, Field


class ParsedDocument(BaseModel):
    """
    Acts as the standard Data Transfer Object (DTO) for passing
    parsed markdown results across system boundaries.
    """

    markdown_content: str = Field(..., description="The extracted markdown text")
    char_count: int = Field(..., description="Total characters extracted")
    elapsed_seconds: float = Field(..., description="Time taken to parse the document")
