# Stage 1: Build stage with uv
FROM astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation for faster startup times
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first to leverage Docker layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY . /app

# Sync project code into virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Stage 2: Final lightweight production image
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy virtual environment and app code from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Place virtualenv executables at top of PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Default command for production (overridden by compose for dev)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]