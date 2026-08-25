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

# Test production image locally with running infrastructure
test-prod:
	@echo "Starting infrastructure in background..."
	docker compose -f docker/docker-compose.yml up -d db redis qdrant
	@echo "Running production container..."
	docker run --rm -it \
		--network docker_default \
		-p 8000:8000 \
		-e ENVIRONMENT=production \
		-e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app_db \
		-e REDIS_URL=redis://redis:6379/0 \
		-e QDRANT_HOST=qdrant \
		-e QDRANT_PORT=6333 \
		backend-app:prod

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
