"""Domain-specific exceptions for the User module."""


class EmailAlreadyExistsError(Exception):
    """Raised when attempting to register an email that is already in use."""
