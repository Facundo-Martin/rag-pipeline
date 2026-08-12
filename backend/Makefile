.PHONY: dev test lint format

dev:
	uv run fastapi dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .