## Scaffolding project

Project structure is intiialized with the following one-shot command:

```bash
mkdir -p alembic/versions \
         docker \
         src/api/v1 \
         src/core \
         src/infrastructure/postgres \
         src/infrastructure/qdrant \
         src/infrastructure/redis \
         src/infrastructure/storage \
         src/modules/auth \
         src/modules/users \
         src/modules/billing \
         src/modules/search \
         tests/unit \
         tests/integration && \
touch alembic/env.py \
      alembic/versions/.gitkeep \
      docker/Dockerfile \
      docker/Dockerfile.dev \
      docker/docker-compose.yml \
      src/__init__.py \
      src/main.py \
      src/config.py \
      src/dependencies.py \
      src/api/__init__.py \
      src/api/v1/__init__.py \
      src/api/v1/health.py \
      src/api/v1/router.py \
      src/core/__init__.py \
      src/core/security.py \
      src/core/exceptions.py \
      src/core/middleware.py \
      src/core/rate_limit.py \
      src/infrastructure/__init__.py \
      src/infrastructure/postgres/__init__.py \
      src/infrastructure/postgres/session.py \
      src/infrastructure/postgres/base.py \
      src/infrastructure/qdrant/__init__.py \
      src/infrastructure/qdrant/client.py \
      src/infrastructure/redis/__init__.py \
      src/infrastructure/redis/client.py \
      src/infrastructure/storage/__init__.py \
      src/infrastructure/storage/s3.py \
      src/modules/__init__.py \
      src/modules/auth/__init__.py \
      src/modules/auth/router.py \
      src/modules/auth/schemas.py \
      src/modules/auth/service.py \
      src/modules/users/__init__.py \
      src/modules/users/router.py \
      src/modules/users/schemas.py \
      src/modules/users/models.py \
      src/modules/users/service.py \
      src/modules/users/dependencies.py \
      src/modules/users/exceptions.py \
      src/modules/billing/__init__.py \
      src/modules/billing/router.py \
      src/modules/billing/schemas.py \
      src/modules/billing/models.py \
      src/modules/billing/service.py \
      src/modules/billing/dependencies.py \
      src/modules/search/__init__.py \
      src/modules/search/router.py \
      src/modules/search/schemas.py \
      src/modules/search/service.py \
      tests/__init__.py \
      tests/conftest.py \
      tests/unit/__init__.py \
      tests/integration/__init__.py \
      .env.example \
      .gitignore \
      pyproject.toml \
      README.md && \
cat > docker/Dockerfile <<'EOF'
FROM python:3.12-slim

# Temporary placeholder until the real production image is defined.
EOF
cat > docker/Dockerfile.dev <<'EOF'
FROM python:3.12-slim

# Temporary placeholder until the real dev image is defined.
EOF
```

TODO: This script over-wrote my pyproject.toml file, which it shouldn't have done... fix it

## FastAPI Dev

Our FastAPI entrypoint is specified in pyproject.toml, according to the official [docs](https://fastapi.tiangolo.com/tutorial/first-steps/#configure-the-app-entrypoint-in-pyproject-toml):

```python
# pyproject.toml

[tool.fastapi]
entrypoint = "src.main:app"
```

Additionally, to simplify development, we are serving it with a Makefile, making it trivial to run the app with `make dev`

```
.PHONY: dev test lint format

dev:
	uv run fastapi dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
```

## Docker development

Makefile was updated. Running make dev now spins up docker container for development
