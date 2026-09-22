set working-directory := ".."

default:
    @just --list docs

# Serve the MkDocs documentation site locally with live-reload
serve:
    uv run mkdocs serve || uv run mkdocs serve -a localhost:8001

# Kill any process on port 8000 and serve MkDocs
serve-force:
    -lsof -ti:8000 | xargs kill -9
    uv run mkdocs serve

# Generate architecture diagrams
diagrams:
    @echo "Generating architecture diagrams..."
    @for file in docs/_diagrams/*.py; do uv run python "$$file"; done
    @echo "Diagrams generated successfully!"
