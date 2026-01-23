---
name: coding-standards
description: Universal coding standards, best practices, and patterns for Python development with FastAPI, SQLAlchemy, and Pydantic.
---

# Coding Standards & Best Practices

Universal coding standards applicable across all Python projects.

## When to Activate

- Starting a new project or module
- Reviewing code for quality and maintainability
- Refactoring existing code to follow conventions
- Enforcing naming, formatting, or structural consistency
- Setting up linting, formatting, or type-checking rules
- Onboarding new contributors to coding conventions

## Code Quality Principles

### 1. Readability First
- Code is read more than written
- Clear variable and function names
- Self-documenting code preferred over comments
- Consistent formatting (ruff)

### 2. KISS (Keep It Simple, Stupid)
- Simplest solution that works
- Avoid over-engineering
- No premature optimization
- Easy to understand > clever code

### 3. DRY (Don't Repeat Yourself)
- Extract common logic into functions
- Create reusable modules
- Share utilities across packages
- Avoid copy-paste programming

### 4. YAGNI (You Aren't Gonna Need It)
- Don't build features before they're needed
- Avoid speculative generality
- Add complexity only when required
- Start simple, refactor when needed

## Python Standards

### Variable Naming

```python
# ✅ GOOD: Descriptive names
market_search_query = "election"
is_user_authenticated = True
total_revenue = 1000

# ❌ BAD: Unclear names
q = "election"
flag = True
x = 1000
```

### Function Naming

```python
# ✅ GOOD: Verb-noun pattern with type hints
async def fetch_market_data(market_id: str) -> Market:
    ...

def calculate_similarity(a: list[float], b: list[float]) -> float:
    ...

def is_valid_email(email: str) -> bool:
    ...

# ❌ BAD: Unclear or noun-only
async def market(id):
    ...

def similarity(a, b):
    ...
```

### Immutability Pattern (CRITICAL)

```python
from dataclasses import dataclass, replace

# ✅ ALWAYS use immutable patterns
@dataclass(frozen=True)
class User:
    name: str
    email: str

def update_user(user: User, name: str) -> User:
    return replace(user, name=name)

# For dicts, create new copies
updated_user = {**user, "name": "New Name"}
updated_list = [*items, new_item]

# ❌ NEVER mutate directly
user["name"] = "New Name"  # BAD
items.append(new_item)      # BAD
```

### Error Handling

```python
import logging

logger = logging.getLogger(__name__)

# ✅ GOOD: Comprehensive error handling
async def fetch_data(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("HTTP error: %s", e)
        raise AppError(f"HTTP {e.response.status_code}") from e
    except Exception as e:
        logger.exception("Fetch failed")
        raise AppError("Failed to fetch data") from e

# ❌ BAD: No error handling
async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Async Best Practices

```python
import asyncio

# ✅ GOOD: Parallel execution when possible
users, markets, stats = await asyncio.gather(
    fetch_users(),
    fetch_markets(),
    fetch_stats()
)

# ❌ BAD: Sequential when unnecessary
users = await fetch_users()
markets = await fetch_markets()
stats = await fetch_stats()
```

### Type Safety

```python
from typing import Protocol
from pydantic import BaseModel

# ✅ GOOD: Proper types with Pydantic
class Market(BaseModel):
    id: str
    name: str
    status: Literal["active", "resolved", "closed"]
    created_at: datetime

def get_market(id: str) -> Market | None:
    ...

# ❌ BAD: Using Any or no types
def get_market(id):  # No types!
    ...
```

## FastAPI Best Practices

### Route Structure

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/markets", tags=["markets"])

@router.get("/{market_id}", response_model=MarketResponse)
async def get_market(
    market_id: str,
    db: Session = Depends(get_db),
) -> MarketResponse:
    """Get market by ID."""
    market = await db.query(Market).filter(Market.id == market_id).first()

    if not market:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market not found"
        )

    return MarketResponse.model_validate(market)
```

### Dependency Injection

```python
from typing import Annotated
from fastapi import Depends

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("/", response_model=MarketResponse)
async def create_market(
    data: MarketCreate,
    db: DbSession,
    user: CurrentUser,
) -> MarketResponse:
    ...
```

## API Design Standards

### REST API Conventions

```
GET    /api/markets              # List all markets
GET    /api/markets/{id}         # Get specific market
POST   /api/markets              # Create new market
PUT    /api/markets/{id}         # Update market (full)
PATCH  /api/markets/{id}         # Update market (partial)
DELETE /api/markets/{id}         # Delete market

# Query parameters for filtering
GET /api/markets?status=active&limit=10&offset=0
```

### Response Format

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None
    meta: PaginationMeta | None = None
```

### Input Validation

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class CreateMarketSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    end_date: datetime
    categories: list[str] = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

## File Organization

### Project Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app
│   └── api/
│       ├── __init__.py
│       ├── deps.py            # Dependencies
│       └── routes/
│           ├── __init__.py
│           ├── markets.py
│           └── users.py
├── core/
│   ├── __init__.py
│   ├── config.py              # Settings
│   └── security.py
├── models/
│   ├── __init__.py
│   └── market.py
├── schemas/
│   ├── __init__.py
│   └── market.py
├── services/
│   ├── __init__.py
│   └── market_service.py
└── repositories/
    ├── __init__.py
    └── market_repository.py
```

### File Naming

```
models/market.py              # snake_case for files
schemas/market.py
services/market_service.py
repositories/market_repository.py
```

## Comments & Documentation

### When to Comment

```python
# ✅ GOOD: Explain WHY, not WHAT
# Use exponential backoff to avoid overwhelming the API during outages
delay = min(1000 * (2 ** retry_count), 30000)

# Deliberately using mutation here for performance with large arrays
items.append(new_item)

# ❌ BAD: Stating the obvious
# Increment counter by 1
count += 1
```

### Docstrings for Public APIs

```python
async def search_markets(
    query: str,
    limit: int = 10
) -> list[Market]:
    """Search markets using semantic similarity.

    Args:
        query: Natural language search query
        limit: Maximum number of results (default: 10)

    Returns:
        Array of markets sorted by similarity score

    Raises:
        AppError: If OpenAI API fails or Redis unavailable

    Example:
        >>> results = await search_markets("election", 5)
        >>> print(results[0].name)
        "Trump vs Biden"
    """
```

## Testing Standards

### Test Structure (AAA Pattern)

```python
import pytest

class TestMarketService:
    def test_creates_market_with_valid_data(self) -> None:
        # Arrange
        service = MarketService()
        data = {"name": "Test", "description": "Test market"}

        # Act
        result = service.create_market(data)

        # Assert
        assert result.name == "Test"

    def test_raises_on_invalid_name(self) -> None:
        # Arrange
        service = MarketService()
        data = {"name": "", "description": "Test"}

        # Act & Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_market(data)
```

## Code Smell Detection

Watch for these anti-patterns:

### 1. Long Functions
```python
# ❌ BAD: Function > 30 lines
def process_market_data():
    # 50 lines of code
    ...

# ✅ GOOD: Split into smaller functions
def process_market_data():
    validated = validate_data()
    transformed = transform_data(validated)
    return save_data(transformed)
```

### 2. Deep Nesting
```python
# ❌ BAD: 4+ levels of nesting
if user:
    if user.is_admin:
        if market:
            if market.is_active:
                # Do something

# ✅ GOOD: Early returns
if not user:
    return
if not user.is_admin:
    return
if not market:
    return
if not market.is_active:
    return
# Do something
```

### 3. Magic Numbers
```python
# ❌ BAD: Unexplained numbers
if retry_count > 3:
    ...
await asyncio.sleep(0.5)

# ✅ GOOD: Named constants
MAX_RETRIES = 3
DEBOUNCE_DELAY_SECONDS = 0.5

if retry_count > MAX_RETRIES:
    ...
await asyncio.sleep(DEBOUNCE_DELAY_SECONDS)
```

**Remember**: Code quality is not negotiable. Clear, maintainable code enables rapid development and confident refactoring.
