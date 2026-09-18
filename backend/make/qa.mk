.PHONY: lint-docker test lint format

# Lint Dockerfiles using official Hadolint container (no local installation needed)
lint-docker:
	docker run --rm -v "$(shell pwd):/work" -w /work hadolint/hadolint hadolint docker/Dockerfile.dev docker/Dockerfile

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .
