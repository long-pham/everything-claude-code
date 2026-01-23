# Security Guidelines (TypeScript/JavaScript)

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized HTML)
- [ ] CSRF protection enabled
- [ ] Authentication/authorization verified
- [ ] Rate limiting on all endpoints
- [ ] Error messages don't leak sensitive data

## Secret Management

```typescript
// NEVER: Hardcoded secrets
const apiKey = "sk-proj-xxxxx"

// ALWAYS: Environment variables
const apiKey = process.env.OPENAI_API_KEY

if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

## Input Validation (Zod)

```typescript
import { z } from 'zod'

const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

const validated = UserSchema.parse(userInput)
```

## XSS Prevention

```typescript
// NEVER: Direct HTML injection
element.innerHTML = userInput  // NO!

// ALWAYS: Use textContent or sanitize
element.textContent = userInput

// Or use DOMPurify for rich content
import DOMPurify from 'dompurify'
element.innerHTML = DOMPurify.sanitize(userInput)
```

## SQL Injection Prevention

```typescript
// NEVER: String interpolation
const query = `SELECT * FROM users WHERE id = '${userId}'`  // NO!

// ALWAYS: Parameterized queries
const result = await db.query('SELECT * FROM users WHERE id = $1', [userId])

// Or use an ORM
const user = await prisma.user.findUnique({ where: { id: userId } })
```

## Security Response Protocol

If security issue found:
1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues
