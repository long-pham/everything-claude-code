# Testing Requirements (TypeScript/JavaScript)

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Individual functions, utilities, components
2. **Integration Tests** - API endpoints, database operations
3. **E2E Tests** - Critical user flows (Playwright)

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Jest/Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      threshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

## Test Structure (AAA Pattern)

```typescript
import { describe, it, expect } from 'vitest'

describe('UserService', () => {
  it('should create user with valid data', async () => {
    // Arrange
    const service = new UserService()
    const data = { name: 'John', email: 'john@example.com' }

    // Act
    const result = await service.createUser(data)

    // Assert
    expect(result.name).toBe('John')
  })

  it('should throw on invalid email', async () => {
    // Arrange
    const service = new UserService()
    const data = { name: 'John', email: 'invalid' }

    // Act & Assert
    await expect(service.createUser(data)).rejects.toThrow('Invalid email')
  })
})
```

## CLI Commands

```bash
npm run test                    # Run all tests
npm run test -- --coverage      # With coverage
npm run test -- --watch         # Watch mode
npx playwright test             # E2E tests
```

## Troubleshooting Test Failures

1. Use **tdd-guide** agent
2. Check test isolation
3. Verify mocks are correct
4. Fix implementation, not tests (unless tests are wrong)

## Agent Support

- **tdd-guide** - Use PROACTIVELY for new features, enforces write-tests-first
- **e2e-runner** - Playwright E2E testing specialist
