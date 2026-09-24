import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_transaction_commits_to_savepoint(db_session):
    """Inserts a record and commits it to the transaction savepoint."""
    await db_session.execute(
        text(
            "INSERT INTO arxiv_documents "
            "(arxiv_id, title, summary, markdown_content, pdf_url, published_date) "
            "VALUES ('ISOLATION-TEST-1', 'Test Title', 'Test summary', "
            "'# Markdown', 'http://example.com/x.pdf', '2024-01-01T00:00:00Z')"
        )
    )
    # This commit should only hit the transaction savepoint, not the physical database
    await db_session.commit()

    # Verify it exists within this test's context
    result = await db_session.execute(
        text("SELECT arxiv_id FROM arxiv_documents WHERE arxiv_id = 'ISOLATION-TEST-1'")
    )
    assert result.scalar() == "ISOLATION-TEST-1"


@pytest.mark.asyncio
async def test_transaction_is_rolled_back(db_session):
    """
    Since this runs after the previous test, the database should be completely empty
    if the conftest.py rollback is working correctly.
    """
    result = await db_session.execute(
        text("SELECT arxiv_id FROM arxiv_documents WHERE arxiv_id = 'ISOLATION-TEST-1'")
    )
    # If this passes, it proves the previous test's data was successfully wiped
    assert result.scalar() is None
