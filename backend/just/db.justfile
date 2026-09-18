# Generate a new migration script
db-migrate message:
    uv run alembic -c pyproject.toml revision --autogenerate -m "{{message}}"

# Apply all pending migrations
db-upgrade:
    uv run alembic -c pyproject.toml upgrade head
