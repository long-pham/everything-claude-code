# Security Guidelines

## Mandatory Security Checks

Before ANY commit:
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs validated (Pydantic)
- [ ] SQL injection prevention (parameterized queries / ORM)
- [ ] No pickle/eval/exec on user input
- [ ] Dependencies scanned (pip-audit)
- [ ] Authentication/authorization verified
- [ ] Rate limiting on all endpoints
- [ ] Error messages don't leak sensitive data

## Secret Management

```python
# NEVER: Hardcoded secrets
API_KEY = "sk-proj-xxxxx"  # NO!

# ALWAYS: Environment variables with pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    database_url: str
    secret_key: str

    model_config = {"env_file": ".env"}

settings = Settings()

if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY not configured")
```

## Input Validation

```python
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

## SQL Injection Prevention

```python
# NEVER: String formatting
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")  # NO!

# ALWAYS: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# BEST: Use SQLAlchemy ORM
user = session.query(User).filter(User.id == user_id).first()
```

## Dangerous Operations - NEVER on User Input

```python
eval(user_input)       # Code execution
exec(user_input)       # Code execution
pickle.loads(data)     # Arbitrary code execution
yaml.load(data)        # Use yaml.safe_load()
subprocess.shell=True  # Command injection
```

## Dependency Scanning

```bash
uv add --dev pip-audit
uv run pip-audit --strict
```

## Security Response Protocol

If security issue found:
1. STOP immediately
2. Use **security-reviewer** agent
3. Fix CRITICAL issues before continuing
4. Rotate any exposed secrets
5. Review entire codebase for similar issues
