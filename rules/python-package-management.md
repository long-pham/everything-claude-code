# Python Package Management

## Package Manager: uv (MANDATORY)

**ALWAYS** use `uv` for all Python package operations. NEVER use `pip`, `poetry`, or `conda` unless explicitly requested.

## Core Commands

```bash
# Create new project
uv init project-name
cd project-name

# Add dependencies
uv add requests fastapi sqlalchemy

# Add dev dependencies
uv add --dev pytest pytest-cov ruff mypy

# Run scripts
uv run python script.py
uv run pytest

# Sync dependencies
uv sync

# Lock dependencies
uv lock
```

## Project Configuration

```toml
# pyproject.toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]
```

## Dependency Pinning

```bash
# uv.lock is auto-generated - commit to version control
# Export to requirements.txt if needed
uv pip compile pyproject.toml -o requirements.txt
```
