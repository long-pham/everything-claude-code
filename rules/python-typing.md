# Python Type Hints & Static Analysis

## Type Hints (MANDATORY)

ALL functions MUST have complete type annotations.

## Function Signatures

```python
# CORRECT: Full type annotations
def fetch_user(user_id: str) -> User | None:
    """Fetch user by ID."""
    ...

async def process_items(
    items: list[Item],
    batch_size: int = 100,
) -> dict[str, int]:
    """Process items in batches."""
    ...

# WRONG: Missing annotations
def fetch_user(user_id):  # NO!
    ...
```

## Modern Type Hints (Python 3.10+)

```python
# Use built-in types (not typing module)
from collections.abc import Sequence, Mapping, Callable

# Union with pipe operator
def process(value: str | int | None) -> str:
    ...

# Optional is just X | None
def get_user(id: str) -> User | None:  # Not Optional[User]
    ...

# Generic collections with built-in syntax
items: list[str] = []
mapping: dict[str, int] = {}
```

## Mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
show_error_codes = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```

## Type Aliases

```python
from typing import TypeAlias

UserId: TypeAlias = str
JsonDict: TypeAlias = dict[str, Any]
Callback: TypeAlias = Callable[[str, int], bool]
```

## Protocols (Structural Typing)

```python
from typing import Protocol

class Repository(Protocol):
    """Repository interface using structural typing."""

    def find_by_id(self, id: str) -> Model | None: ...
    def save(self, model: Model) -> Model: ...
    def delete(self, id: str) -> None: ...
```

## CLI Commands

```bash
# Run mypy
uv run mypy src/

# With specific config
uv run mypy src/ --config-file pyproject.toml
```
