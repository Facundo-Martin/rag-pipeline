# ==========================================
# Builder Stage
# ==========================================
FROM python:3.14-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set env vars for uv and python
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# First, install dependencies only (--no-dev ensures we don't ship pytest/ruff to prod)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Now copy the rest of the app and sync the project itself
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==========================================
# Final Stage
# ==========================================
FROM python:3.14-slim-bookworm

# 1. Install System Dependencies for Docling/OCR (Bypass Fastly CDN with correct Security routing)
RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    sed -i 's|http://deb.debian.org/debian|http://ftp.us.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|http://deb.debian.org/debian-security|http://security.debian.org/debian-security|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    # Explicit cache directories for the non-root user
    HF_HOME="/home/appuser/.cache/huggingface" \
    DOCLING_HOME="/home/appuser/.cache/docling"

WORKDIR /app

# 3. Create a non-root user and setup cache directories BEFORE switching users
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /home/appuser/.cache/huggingface /home/appuser/.cache/docling && \
    chown -R appuser:appuser /home/appuser/.cache

# 4. Copy the completely self-contained .venv and app from the builder
COPY --from=builder /app /app

# 5. Change ownership of the app directory so the appuser can execute it
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Run with Gunicorn managing Uvicorn workers
CMD ["gunicorn", "src.main:app", "-c", "gunicorn_conf.py"]
