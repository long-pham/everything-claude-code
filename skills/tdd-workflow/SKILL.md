---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage using pytest.
---

# Test-Driven Development Workflow

This skill ensures all code development follows TDD principles with comprehensive test coverage.

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints
- Creating new services or modules

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements
- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. Test Types

#### Unit Tests
- Individual functions and utilities
- Class methods
- Pure functions
- Helpers and utilities

#### Integration Tests
- API endpoints
- Database operations
- Service interactions
- External API calls

#### E2E Tests
- Critical user flows
- Complete workflows
- API automation

## TDD Workflow Steps

### Step 1: Write User Journeys
```
As a [role], I want to [action], so that [benefit]

Example:
As a user, I want to search for markets semantically,
so that I can find relevant markets even without exact keywords.
```

### Step 2: Generate Test Cases
For each user journey, create comprehensive test cases:

```python
import pytest
from my_project.services import MarketService


class TestSemanticSearch:
    async def test_returns_relevant_markets_for_query(self) -> None:
        # Test implementation
        ...

    async def test_handles_empty_query_gracefully(self) -> None:
        # Test edge case
        ...

    async def test_falls_back_when_redis_unavailable(self) -> None:
        # Test fallback behavior
        ...

    async def test_sorts_results_by_similarity_score(self) -> None:
        # Test sorting logic
        ...
```

### Step 3: Run Tests (They Should Fail)
```bash
uv run pytest
# Tests should fail - we haven't implemented yet
```

### Step 4: Implement Code
Write minimal code to make tests pass:

```python
async def search_markets(query: str) -> list[Market]:
    """Implementation guided by tests."""
    ...
```

### Step 5: Run Tests Again
```bash
uv run pytest
# Tests should now pass
```

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance
- Enhance readability

### Step 7: Verify Coverage
```bash
uv run pytest --cov=src --cov-report=html
# Verify 80%+ coverage achieved
```

## Testing Patterns

### Unit Test Pattern (pytest)
```python
import pytest
from my_project.services import UserService


class TestUserService:
    def test_creates_user_with_valid_data(self) -> None:
        # Arrange
        service = UserService()
        data = {"name": "John", "email": "john@example.com"}

        # Act
        result = service.create_user(data)

        # Assert
        assert result.name == "John"
        assert result.email == "john@example.com"

    def test_raises_on_invalid_email(self) -> None:
        # Arrange
        service = UserService()
        data = {"name": "John", "email": "invalid"}

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email"):
            service.create_user(data)
```

### API Integration Test Pattern
```python
import pytest
from httpx import AsyncClient
from my_project.main import app


@pytest.mark.asyncio
class TestMarketsAPI:
    async def test_returns_markets_successfully(self) -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/markets")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

    async def test_validates_query_parameters(self) -> None:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/markets?limit=invalid")

        assert response.status_code == 422

    async def test_handles_database_errors_gracefully(self) -> None:
        # Mock database failure
        ...
```

### E2E Test Pattern (pytest + httpx)
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.e2e
class TestMarketFlow:
    async def test_user_can_search_and_filter_markets(
        self, authenticated_client: AsyncClient
    ) -> None:
        # Search for markets
        response = await authenticated_client.get(
            "/api/markets/search",
            params={"q": "election"}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) > 0
        assert "election" in data["data"][0]["name"].lower()

    async def test_user_can_create_market(
        self, authenticated_client: AsyncClient
    ) -> None:
        # Create market
        response = await authenticated_client.post(
            "/api/markets",
            json={
                "name": "Test Market",
                "description": "Test description",
                "end_date": "2025-12-31T00:00:00Z"
            }
        )
        assert response.status_code == 201

        data = response.json()
        assert data["data"]["name"] == "Test Market"
```

## Test File Organization

```
src/
├── my_project/
│   ├── services/
│   │   └── user_service.py
│   └── api/
│       └── routes/
│           └── markets.py
tests/
├── __init__.py
├── conftest.py                    # Fixtures
├── unit/
│   ├── __init__.py
│   └── test_user_service.py       # Unit tests
├── integration/
│   ├── __init__.py
│   └── test_markets_api.py        # Integration tests
└── e2e/
    ├── __init__.py
    └── test_market_flow.py        # E2E tests
```

## Fixtures (conftest.py)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from my_project.core.database import Base


@pytest.fixture
def db_session() -> Session:
    """Create a database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def user_service(db_session: Session) -> UserService:
    """Create UserService with test database."""
    return UserService(db_session)


@pytest.fixture
async def authenticated_client() -> AsyncClient:
    """Create authenticated test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Add auth token
        client.headers["Authorization"] = f"Bearer {test_token}"
        yield client
```

## Mocking External Services

### Database Mock
```python
from unittest.mock import AsyncMock, patch


@patch("my_project.repositories.market_repository.Session")
async def test_with_mocked_db(mock_session: AsyncMock) -> None:
    mock_session.query.return_value.filter.return_value.first.return_value = Market(
        id="1", name="Test Market"
    )

    result = await get_market("1")
    assert result.name == "Test Market"
```

### Redis Mock
```python
@patch("my_project.services.cache.redis_client")
async def test_with_mocked_redis(mock_redis: AsyncMock) -> None:
    mock_redis.get.return_value = '{"id": "1", "name": "Cached Market"}'

    result = await get_cached_market("1")
    assert result["name"] == "Cached Market"
```

### External API Mock
```python
@patch("my_project.services.openai_service.client")
async def test_with_mocked_openai(mock_client: AsyncMock) -> None:
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    )

    result = await generate_embedding("test query")
    assert len(result) == 1536
```

## pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = ["-ra", "-q", "--strict-markers", "-vv"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## Common Testing Mistakes to Avoid

### ❌ WRONG: Testing Implementation Details
```python
# Don't test internal state
assert service._internal_cache["key"] == value
```

### ✅ CORRECT: Test Observable Behavior
```python
# Test what users/callers observe
result = service.get_value("key")
assert result == expected_value
```

### ❌ WRONG: No Test Isolation
```python
# Tests depend on each other
def test_creates_user():
    ...

def test_updates_same_user():
    # depends on previous test
    ...
```

### ✅ CORRECT: Independent Tests
```python
# Each test sets up its own data
def test_creates_user(user_factory):
    user = user_factory()
    ...

def test_updates_user(user_factory):
    user = user_factory()
    ...
```

## CLI Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_user_service.py

# Run specific test
uv run pytest tests/unit/test_user_service.py::TestUserService::test_creates_user

# Run with markers
uv run pytest -m "not slow"
uv run pytest -m integration
uv run pytest -m e2e

# Watch mode (with pytest-watch)
uv run ptw
```

## Best Practices

1. **Write Tests First** - Always TDD
2. **One Assert Per Test** - Focus on single behavior
3. **Descriptive Test Names** - Explain what's tested
4. **Arrange-Act-Assert** - Clear test structure
5. **Mock External Dependencies** - Isolate unit tests
6. **Test Edge Cases** - None, empty, large values
7. **Test Error Paths** - Not just happy paths
8. **Keep Tests Fast** - Unit tests < 50ms each
9. **Clean Up After Tests** - No side effects
10. **Review Coverage Reports** - Identify gaps

## Success Metrics

- 80%+ code coverage achieved
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution (< 30s for unit tests)
- E2E tests cover critical user flows
- Tests catch bugs before production

---

**Remember**: Tests are not optional. They are the safety net that enables confident refactoring, rapid development, and production reliability.
