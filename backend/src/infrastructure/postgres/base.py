from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Modern SQLAlchemy 2.0 Declarative Base.
    All database models will inherit from this class.
    """
