# Run the test suite
test:
    uv run pytest -v

# Lint the codebase
lint:
    uv run ruff check .

# Format the codebase
format:
    uv run ruff check --fix .
    uv run ruff format .

# Lint Dockerfiles
lint-docker:
    docker run --rm -v "{{invocation_directory()}}:/work" -w /work hadolint/hadolint hadolint docker/Dockerfile.dev docker/Dockerfile
