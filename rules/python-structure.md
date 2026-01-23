# Python Project Structure

## Standard Layout

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── users.py
│       │   │   └── items.py
│       │   └── deps.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── security.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── user_service.py
│       └── repositories/
│           ├── __init__.py
│           └── user_repository.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── test_services.py
│   ├── integration/
│   │   └── test_api.py
│   └── e2e/
│       └── test_flows.py
├── pyproject.toml
├── uv.lock
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

## File Organization Rules

- **Many small files** over few large files
- **200-400 lines** typical, **500 max** per file
- **One class per file** for models/schemas
- **Group by feature**, not by type

## Naming Conventions

```python
# Files: snake_case
user_service.py
user_repository.py

# Classes: PascalCase
class UserService:
    ...

class UserRepository:
    ...

# Functions/variables: snake_case
def get_user_by_id(user_id: str) -> User:
    ...

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private: leading underscore
def _internal_helper() -> None:
    ...
```

## Import Organization

```python
# 1. Standard library
import os
from collections.abc import Callable
from pathlib import Path

# 2. Third-party
import httpx
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

# 3. Local
from my_project.core.config import settings
from my_project.models.user import User
from my_project.services.user_service import UserService
```
