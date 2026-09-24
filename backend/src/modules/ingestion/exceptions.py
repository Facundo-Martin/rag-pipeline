"""Domain-specific exceptions for the Ingestion module."""

from fastapi import status

from src.core.exceptions import AppException


class DocumentAlreadyExistsError(AppException):
    """Raised when attempting to ingest an ArXiv paper that is already in the database."""

    def __init__(self, arxiv_id: str) -> None:
        super().__init__(
            message=f"ArXiv document {arxiv_id} is already ingested.",
            status_code=status.HTTP_409_CONFLICT,
        )
