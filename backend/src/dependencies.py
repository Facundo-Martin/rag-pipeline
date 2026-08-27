from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Import the generator we just built
from src.infrastructure.postgres.session import get_db_session

# Create a highly readable type alias for database injection
DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# TODO: Add Redis and Qdrant here
