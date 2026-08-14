.PHONY: dev lint-docker down build test logs clean

# Start all containers in development mode
dev:
	docker compose up --build

# Lint Dockerfiles using official Hadolint container (no local installation needed)
lint-docker:
	docker run --rm -v "$(shell pwd):/work" -w /work hadolint/hadolint hadolint docker/Dockerfile.dev docker/Dockerfile

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

# Start containers in background (detached)
dev-d:
	docker compose up -d

# Stop all running containers
down:
	docker compose down

# Rebuild containers from scratch
build:
	docker compose up --build

# View container logs
logs:
	docker compose logs -f app

# Run pytest inside local environment


# Clean up temp files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +