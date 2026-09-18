.PHONY: db-migrate db-upgrade

# Generate a new migration script (Usage: make db-migrate msg="added users table")
db-migrate:
	uv run alembic -c pyproject.toml revision --autogenerate -m "$(msg)"

# Apply all pending migrations to the database
db-upgrade:
	uv run alembic -c pyproject.toml upgrade head
