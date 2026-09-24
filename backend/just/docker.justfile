set working-directory := ".."
export COMPOSE_BAKE := "true"

default:
    @just --list docker

# Start all containers in development mode AND serve documentation
dev:
    @echo "Starting Docker infrastructure in the background..."
    docker compose -f docker/docker-compose.yml up --build -d
    @echo "Starting MkDocs documentation server..."
    uv run mkdocs serve || uv run mkdocs serve -a localhost:8001 || uv run mkdocs serve -a localhost:8002

# Start containers in background (detached)
dev-d:
    docker compose -f docker/docker-compose.yml up -d

# Stop all running containers
down:
    docker compose -f docker/docker-compose.yml down

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
    docker run --rm -it --network docker_default -p 8000:8000 -e ENVIRONMENT=production -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app_db backend-app:prod

# View container logs
logs:
    docker compose -f docker/docker-compose.yml logs -f app
