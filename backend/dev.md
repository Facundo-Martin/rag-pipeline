## Scaffolding project

To one-shot the project folder structure with our modular monolith vertical slice design, we do:

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

## Init FastAPI backend

To init the FastAPI backend and configure it we do:

```bash
# Initialize the project (this will update pyproject.toml)
uv init

# Add FastAPI (with standard ASGI server tools), Pydantic for validation, and Pydantic-Settings for config
uv add "fastapi[standard]" pydantic pydantic-settings
```

Then we create some dummy code in our main.py function:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

And we run the application with:

```bash
uv run fastapi dev src/main.py
```

Now, because we don't want to specify this entry point every single time, we can confdigure the app entrypoint as stated in the [docs](https://fastapi.tiangolo.com/tutorial/first-steps/#configure-the-app-entrypoint-in-pyproject-toml):

```python
# pyproject.toml

[tool.fastapi]
entrypoint = "src.main:app"
```

Alternatively, we can create a makefile to simplify this process
