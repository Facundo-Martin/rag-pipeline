default:
    @just --list docs

# Generate architecture diagrams
diagrams:
    @echo "Generating architecture diagrams..."
    @for file in docs/_diagrams/*.py; do uv run python "$$file"; done
    @echo "Diagrams generated successfully!"
