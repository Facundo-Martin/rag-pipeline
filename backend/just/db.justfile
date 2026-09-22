default:
    @just --list db

# Generate a new migration script
migrate message:
    uv run alembic -c pyproject.toml revision --autogenerate -m "{{message}}"

# Apply all pending migrations
upgrade:
    uv run alembic -c pyproject.toml upgrade head
