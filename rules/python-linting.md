# Python Linting & Formatting

## Ruff (MANDATORY)

Use **ruff** for both linting and formatting. It replaces black, isort, flake8.

## Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
exclude = [".venv", "__pycache__", ".git", "migrations"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific rules
]
ignore = ["E501", "PLR0913"]
fixable = ["ALL"]

[tool.ruff.lint.isort]
known-first-party = ["my_project"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## CLI Commands

```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without modifying
uv run ruff format --check .
```

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Critical Rules

- **No commented-out code** (ERA001)
- **No unused imports** (F401)
- **No unused variables** (F841)
- **Use pathlib over os.path** (PTH)
- **Simplify boolean expressions** (SIM)
- **Use modern Python syntax** (UP)
