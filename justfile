# Run the gate and installer tests
test:
    uv run pytest -q

# Lint, format-check and type-check
lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run ty check

# Install the harness into another repo: just install ~/projects/my-app
install target:
    uv run install.py {{target}}
