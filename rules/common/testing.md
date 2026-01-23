# Testing Requirements

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Individual functions, utilities, classes
2. **Integration Tests** - API endpoints, database operations
3. **E2E Tests** - Critical user flows (pytest + httpx/playwright)

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

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
]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Test Structure (AAA Pattern)

```python
import pytest

class TestUserService:
    def test_create_user_with_valid_data(self) -> None:
        # Arrange
        service = UserService()
        data = {"name": "John", "email": "john@example.com"}

        # Act
        result = service.create_user(data)

        # Assert
        assert result.name == "John"

    def test_create_user_raises_on_invalid_email(self) -> None:
        # Arrange
        service = UserService()
        data = {"name": "John", "email": "invalid"}

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email"):
            service.create_user(data)
```

## CLI Commands

```bash
uv run pytest                           # Run all tests
uv run pytest --cov=src --cov-report=html  # With coverage
uv run pytest -m "not slow"             # Skip slow tests
uv run pytest -k "test_create"          # Run matching tests
```

## Troubleshooting Test Failures

1. Use **tdd-guide** agent
2. Check test isolation
3. Verify mocks are correct
4. Fix implementation, not tests (unless tests are wrong)

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features, enforces write-tests-first
- **e2e-runner** - E2E testing specialist
