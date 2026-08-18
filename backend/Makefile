.PHONY: dev dev-d down build build-prod test lint format lint-docker logs clean

# Start all containers in development mode
dev:
	docker compose -f docker/docker-compose.yml up --build

# Start containers in background (detached)
dev-d:
	docker compose -f docker/docker-compose.yml up -d

# Rebuild dev containers from scratch
build:
	docker compose -f docker/docker-compose.yml up --build

# Build production Docker image locally
build-prod:
	docker build -f docker/Dockerfile -t backend-app:prod .

# Lint Dockerfiles using official Hadolint container (no local installation needed)
lint-docker:
	docker run --rm -v "$(shell pwd):/work" -w /work hadolint/hadolint hadolint docker/Dockerfile.dev docker/Dockerfile

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

# Stop all running containers
down:
	docker compose -f docker/docker-compose.yml down

# View container logs
logs:
	docker compose -f docker/docker-compose.yml logs -f app

# Clean up temp files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
