---
name: security-review
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns for Python/FastAPI.
---

# Security Review Skill

This skill ensures all code follows security best practices and identifies potential vulnerabilities.

## When to Activate

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating new API endpoints
- Working with secrets or credentials
- Implementing payment features
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Security Checklist

### 1. Secrets Management

#### ❌ NEVER Do This
```python
API_KEY = "sk-proj-xxxxx"  # Hardcoded secret
DB_PASSWORD = "password123"  # In source code
```

#### ✅ ALWAYS Do This
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    database_url: str
    secret_key: str

    model_config = {"env_file": ".env"}


settings = Settings()

# Verify secrets exist at startup
if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY not configured")
```

#### Verification Steps
- [ ] No hardcoded API keys, tokens, or passwords
- [ ] All secrets in environment variables
- [ ] `.env` in .gitignore
- [ ] No secrets in git history
- [ ] Production secrets in hosting platform

### 2. Input Validation

#### Always Validate User Input with Pydantic
```python
from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUserSchema(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


@router.post("/users")
async def create_user(data: CreateUserSchema) -> UserResponse:
    # data is already validated
    return await user_service.create(data)
```

#### File Upload Validation
```python
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}


async def validate_file_upload(file: UploadFile) -> None:
    # Type check
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    # Extension check
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, "Invalid file extension")

    # Size check (read in chunks)
    size = 0
    while chunk := await file.read(8192):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large (max 5MB)")

    await file.seek(0)  # Reset for later reading
```

#### Verification Steps
- [ ] All user inputs validated with Pydantic
- [ ] File uploads restricted (size, type, extension)
- [ ] No direct use of user input in queries
- [ ] Whitelist validation (not blacklist)
- [ ] Error messages don't leak sensitive info

### 3. SQL Injection Prevention

#### ❌ NEVER Concatenate SQL
```python
# DANGEROUS - SQL Injection vulnerability
query = f"SELECT * FROM users WHERE email = '{user_email}'"
cursor.execute(query)
```

#### ✅ ALWAYS Use Parameterized Queries
```python
# Safe - parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (user_email,)
)

# Or with SQLAlchemy ORM (preferred)
user = session.query(User).filter(User.email == user_email).first()
```

#### Verification Steps
- [ ] All database queries use parameterized queries
- [ ] No string concatenation/formatting in SQL
- [ ] SQLAlchemy ORM used correctly
- [ ] No raw SQL with user input

### 4. Authentication & Authorization

#### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

#### JWT Token Handling
```python
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    user = await get_user(user_id)
    if not user:
        raise HTTPException(401, "User not found")

    return user
```

#### Authorization Checks
```python
from enum import Enum


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


def require_permission(permission: Permission):
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if permission not in user.permissions:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return Depends(dependency)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = require_permission(Permission.ADMIN),
) -> dict:
    await user_service.delete(user_id)
    return {"success": True}
```

#### Verification Steps
- [ ] Passwords hashed with bcrypt
- [ ] JWT tokens properly validated
- [ ] Authorization checks before sensitive operations
- [ ] Role-based access control implemented
- [ ] Session management secure

### 5. Dangerous Operations - NEVER on User Input

```python
# ❌ DANGEROUS - Code execution risks
eval(user_input)        # Arbitrary code execution
exec(user_input)        # Arbitrary code execution
pickle.loads(data)      # Arbitrary code execution
yaml.load(data)         # Use yaml.safe_load()
subprocess.run(cmd, shell=True)  # Command injection

# ✅ SAFE alternatives
import ast
ast.literal_eval(user_input)  # Only for literal structures

import yaml
yaml.safe_load(data)  # Safe YAML parsing

import subprocess
subprocess.run([cmd, arg1, arg2], shell=False)  # No shell
```

### 6. Rate Limiting

```python
from fastapi import Request
from collections import defaultdict
from time import time


class RateLimiter:
    def __init__(self) -> None:
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> bool:
        now = time()
        self.requests[key] = [
            t for t in self.requests[key]
            if now - t < window_seconds
        ]

        if len(self.requests[key]) >= max_requests:
            return False

        self.requests[key].append(now)
        return True


limiter = RateLimiter()


@router.get("/api/search")
async def search(request: Request) -> SearchResponse:
    client_ip = request.client.host if request.client else "unknown"

    if not limiter.is_allowed(client_ip, max_requests=10, window_seconds=60):
        raise HTTPException(429, "Rate limit exceeded")

    return await perform_search()
```

#### Verification Steps
- [ ] Rate limiting on all API endpoints
- [ ] Stricter limits on expensive operations
- [ ] IP-based rate limiting
- [ ] User-based rate limiting (authenticated)

### 7. Sensitive Data Exposure

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

# ❌ WRONG: Logging sensitive data
logger.info(f"User login: {email}, {password}")
logger.info(f"Payment: {card_number}, {cvv}")

# ✅ CORRECT: Redact sensitive data
logger.info(f"User login: {email}")
logger.info(f"Payment: card ending {card_last4}")
```

#### Error Messages
```python
# ❌ WRONG: Exposing internal details
except Exception as e:
    return {"error": str(e), "traceback": traceback.format_exc()}

# ✅ CORRECT: Generic error messages
except Exception as e:
    logger.exception("Internal error")
    return {"error": "An error occurred. Please try again."}
```

#### Verification Steps
- [ ] No passwords, tokens, or secrets in logs
- [ ] Error messages generic for users
- [ ] Detailed errors only in server logs
- [ ] No stack traces exposed to users

### 8. Dependency Security

```bash
# Check for vulnerabilities
uv add --dev pip-audit
uv run pip-audit

# Fix automatically
uv run pip-audit --fix

# Check in CI/CD
uv run pip-audit --strict --progress-spinner off
```

#### Verification Steps
- [ ] Dependencies up to date
- [ ] No known vulnerabilities
- [ ] Lock files committed (uv.lock)
- [ ] Regular security updates

### 9. CORS Configuration

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ GOOD: Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://admin.myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ❌ BAD: Allow all origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Never with credentials!
    allow_credentials=True,
)
```

### 10. Security Headers

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)
```

## Security Testing

### Automated Security Tests
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSecurity:
    async def test_requires_authentication(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/api/protected")
        assert response.status_code == 401

    async def test_requires_admin_role(
        self, client: AsyncClient, user_token: str
    ) -> None:
        response = await client.get(
            "/api/admin",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403

    async def test_rejects_invalid_input(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/api/users",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    async def test_enforces_rate_limits(
        self, client: AsyncClient
    ) -> None:
        responses = [
            await client.get("/api/endpoint")
            for _ in range(101)
        ]
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0
```

## Pre-Deployment Security Checklist

Before ANY production deployment:

- [ ] **Secrets**: No hardcoded secrets, all in env vars
- [ ] **Input Validation**: All user inputs validated with Pydantic
- [ ] **SQL Injection**: All queries parameterized (SQLAlchemy ORM)
- [ ] **Authentication**: Proper JWT/session handling
- [ ] **Authorization**: Role checks in place
- [ ] **Rate Limiting**: Enabled on all endpoints
- [ ] **HTTPS**: Enforced in production
- [ ] **Security Headers**: Configured
- [ ] **Error Handling**: No sensitive data in errors
- [ ] **Logging**: No sensitive data logged
- [ ] **Dependencies**: Up to date, no vulnerabilities (pip-audit)
- [ ] **CORS**: Properly configured
- [ ] **File Uploads**: Validated (size, type)
- [ ] **No dangerous operations**: No eval/exec/pickle on user input

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/)

---

**Remember**: Security is not optional. One vulnerability can compromise the entire platform. When in doubt, err on the side of caution.
