# Coding Style

## Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate:

```python
# WRONG: Mutation
def update_user(user: dict, name: str) -> dict:
    user["name"] = name  # MUTATION!
    return user

# CORRECT: Immutability
def update_user(user: dict, name: str) -> dict:
    return {**user, "name": name}

# BETTER: Use dataclasses with replace()
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    email: str

def update_user(user: User, name: str) -> User:
    return replace(user, name=name)
```

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- High cohesion, low coupling
- 200-400 lines typical, 500 max
- Extract utilities from large modules
- Organize by feature/domain, not by type

## Error Handling

ALWAYS handle errors comprehensively:

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await risky_operation()
    return result
except SpecificError as e:
    logger.error("Operation failed: %s", e)
    raise AppError("Detailed user-friendly message") from e
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

## Input Validation

ALWAYS validate user input with Pydantic:

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    name: str = Field(..., min_length=1, max_length=100)

validated = UserCreate.model_validate(input_data)
```

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<30 lines)
- [ ] Files are focused (<500 lines)
- [ ] No deep nesting (>3 levels)
- [ ] Proper error handling
- [ ] No print() statements (use logging)
- [ ] No hardcoded values
- [ ] No mutation (immutable patterns used)
- [ ] All functions have type hints
- [ ] Ruff check passes
