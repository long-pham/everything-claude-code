---
name: backend-patterns
description: Backend architecture patterns, API design, database optimization, and server-side best practices for Python, FastAPI, and SQLAlchemy.
---

# Backend Development Patterns

Backend architecture patterns and best practices for scalable Python server-side applications.

## API Design Patterns

### RESTful API Structure

```python
# ✅ Resource-based URLs
GET    /api/markets                 # List resources
GET    /api/markets/{id}            # Get single resource
POST   /api/markets                 # Create resource
PUT    /api/markets/{id}            # Replace resource
PATCH  /api/markets/{id}            # Update resource
DELETE /api/markets/{id}            # Delete resource

# ✅ Query parameters for filtering, sorting, pagination
GET /api/markets?status=active&sort=volume&limit=20&offset=0
```

### Repository Pattern

```python
from typing import Protocol, TypeVar
from sqlalchemy.orm import Session

T = TypeVar("T")


class Repository(Protocol[T]):
    """Abstract repository interface."""

    async def find_all(self, filters: dict | None = None) -> list[T]: ...
    async def find_by_id(self, id: str) -> T | None: ...
    async def create(self, data: dict) -> T: ...
    async def update(self, id: str, data: dict) -> T: ...
    async def delete(self, id: str) -> None: ...


class SQLAlchemyMarketRepository:
    """SQLAlchemy implementation of MarketRepository."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def find_all(self, filters: dict | None = None) -> list[Market]:
        query = self.session.query(Market)

        if filters:
            if status := filters.get("status"):
                query = query.filter(Market.status == status)
            if limit := filters.get("limit"):
                query = query.limit(limit)

        return query.all()

    async def find_by_id(self, id: str) -> Market | None:
        return self.session.query(Market).filter(Market.id == id).first()
```

### Service Layer Pattern

```python
from dataclasses import dataclass


@dataclass
class MarketService:
    """Business logic separated from data access."""

    repository: MarketRepository

    async def search_markets(self, query: str, limit: int = 10) -> list[Market]:
        # Business logic
        embedding = await generate_embedding(query)
        results = await self._vector_search(embedding, limit)

        # Fetch full data
        market_ids = [r.id for r in results]
        markets = await self.repository.find_by_ids(market_ids)

        # Sort by similarity
        score_map = {r.id: r.score for r in results}
        return sorted(markets, key=lambda m: score_map.get(m.id, 0), reverse=True)

    async def _vector_search(
        self, embedding: list[float], limit: int
    ) -> list[SearchResult]:
        ...
```

### Dependency Injection (FastAPI)

```python
from typing import Annotated
from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_market_repository(
    db: Session = Depends(get_db),
) -> MarketRepository:
    return SQLAlchemyMarketRepository(db)


def get_market_service(
    repository: MarketRepository = Depends(get_market_repository),
) -> MarketService:
    return MarketService(repository=repository)


# Type aliases for cleaner signatures
DbSession = Annotated[Session, Depends(get_db)]
MarketSvc = Annotated[MarketService, Depends(get_market_service)]


@router.get("/markets/{market_id}")
async def get_market(market_id: str, service: MarketSvc) -> MarketResponse:
    market = await service.get_by_id(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return MarketResponse.model_validate(market)
```

## Database Patterns

### Query Optimization

```python
# ✅ GOOD: Select only needed columns
markets = (
    session.query(Market.id, Market.name, Market.status, Market.volume)
    .filter(Market.status == "active")
    .order_by(Market.volume.desc())
    .limit(10)
    .all()
)

# ❌ BAD: Select everything
markets = session.query(Market).all()
```

### N+1 Query Prevention

```python
# ❌ BAD: N+1 query problem
markets = session.query(Market).all()
for market in markets:
    market.creator = session.query(User).get(market.creator_id)  # N queries!

# ✅ GOOD: Eager loading
from sqlalchemy.orm import joinedload

markets = (
    session.query(Market)
    .options(joinedload(Market.creator))  # 1 query with JOIN
    .all()
)

# ✅ GOOD: Batch fetch
markets = session.query(Market).all()
creator_ids = [m.creator_id for m in markets]
creators = session.query(User).filter(User.id.in_(creator_ids)).all()  # 1 query
creator_map = {c.id: c for c in creators}

for market in markets:
    market.creator = creator_map.get(market.creator_id)
```

### Transaction Pattern

```python
from contextlib import contextmanager


@contextmanager
def transaction(session: Session):
    """Context manager for database transactions."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


async def create_market_with_position(
    session: Session,
    market_data: MarketCreate,
    position_data: PositionCreate,
) -> Market:
    with transaction(session):
        market = Market(**market_data.model_dump())
        session.add(market)
        session.flush()  # Get market.id

        position = Position(market_id=market.id, **position_data.model_dump())
        session.add(position)

        return market
```

## Caching Strategies

### Redis Caching Layer

```python
import json
from dataclasses import dataclass

import redis.asyncio as redis


@dataclass
class CachedMarketRepository:
    """Repository with Redis caching layer."""

    base_repo: MarketRepository
    redis: redis.Redis
    ttl: int = 300  # 5 minutes

    async def find_by_id(self, id: str) -> Market | None:
        cache_key = f"market:{id}"

        # Check cache first
        cached = await self.redis.get(cache_key)
        if cached:
            return Market.model_validate_json(cached)

        # Cache miss - fetch from database
        market = await self.base_repo.find_by_id(id)

        if market:
            await self.redis.setex(
                cache_key, self.ttl, market.model_dump_json()
            )

        return market

    async def invalidate_cache(self, id: str) -> None:
        await self.redis.delete(f"market:{id}")
```

### Cache-Aside Pattern

```python
async def get_market_with_cache(
    id: str,
    redis: redis.Redis,
    session: Session,
) -> Market:
    cache_key = f"market:{id}"

    # Try cache
    cached = await redis.get(cache_key)
    if cached:
        return Market.model_validate_json(cached)

    # Cache miss - fetch from DB
    market = session.query(Market).filter(Market.id == id).first()

    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    # Update cache
    await redis.setex(cache_key, 300, market.model_dump_json())

    return market
```

## Error Handling Patterns

### Centralized Error Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class AppError(Exception):
    """Application-specific error."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        is_operational: bool = True,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.is_operational = is_operational
        super().__init__(message)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation failed",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )
```

### Retry with Exponential Backoff

```python
import asyncio
from collections.abc import Callable, Awaitable
from typing import TypeVar

T = TypeVar("T")


async def fetch_with_retry(
    fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
) -> T:
    last_error: Exception | None = None

    for i in range(max_retries):
        try:
            return await fn()
        except Exception as e:
            last_error = e

            if i < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                delay = (2 ** i)
                await asyncio.sleep(delay)

    raise last_error  # type: ignore


# Usage
data = await fetch_with_retry(lambda: fetch_from_api())
```

## Authentication & Authorization

### JWT Token Validation

```python
from datetime import datetime, timedelta

import jwt
from pydantic import BaseModel


class JWTPayload(BaseModel):
    user_id: str
    email: str
    role: Literal["admin", "user"]
    exp: datetime


def create_token(user: User, secret: str) -> str:
    payload = JWTPayload(
        user_id=user.id,
        email=user.email,
        role=user.role,
        exp=datetime.utcnow() + timedelta(hours=24),
    )
    return jwt.encode(payload.model_dump(), secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> JWTPayload:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return JWTPayload.model_validate(payload)
    except jwt.InvalidTokenError as e:
        raise AppError("Invalid token", status_code=401) from e


async def get_current_user(
    authorization: str = Header(...),
    secret: str = Depends(get_secret),
) -> JWTPayload:
    if not authorization.startswith("Bearer "):
        raise AppError("Invalid authorization header", status_code=401)

    token = authorization.replace("Bearer ", "")
    return verify_token(token, secret)
```

### Role-Based Access Control

```python
from enum import Enum
from functools import wraps


class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[str, list[Permission]] = {
    "admin": [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN],
    "moderator": [Permission.READ, Permission.WRITE, Permission.DELETE],
    "user": [Permission.READ, Permission.WRITE],
}


def has_permission(user: JWTPayload, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(user.role, [])


def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: JWTPayload = Depends(get_current_user), **kwargs):
            if not has_permission(user, permission):
                raise AppError("Insufficient permissions", status_code=403)
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# Usage
@router.delete("/markets/{market_id}")
@require_permission(Permission.DELETE)
async def delete_market(market_id: str, user: JWTPayload) -> dict:
    ...
```

## Rate Limiting

```python
from collections import defaultdict
from time import time


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self) -> None:
        self.requests: dict[str, list[float]] = defaultdict(list)

    def check_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        now = time()
        requests = self.requests[identifier]

        # Remove old requests outside window
        requests[:] = [t for t in requests if now - t < window_seconds]

        if len(requests) >= max_requests:
            return False  # Rate limit exceeded

        requests.append(now)
        return True


limiter = RateLimiter()


@router.get("/api/search")
async def search(
    q: str,
    request: Request,
) -> SearchResponse:
    client_ip = request.client.host if request.client else "unknown"

    if not limiter.check_limit(client_ip, max_requests=10, window_seconds=60):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
        )

    return await perform_search(q)
```

## Logging & Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = get_logger(__name__)


# Usage
@router.get("/markets")
async def get_markets(request: Request) -> list[Market]:
    request_id = request.headers.get("X-Request-ID", "unknown")

    logger.info(
        "Fetching markets",
        extra={"request_id": request_id, "path": "/markets"},
    )

    try:
        markets = await fetch_markets()
        return markets
    except Exception as e:
        logger.exception(
            "Failed to fetch markets",
            extra={"request_id": request_id},
        )
        raise
```

**Remember**: Backend patterns enable scalable, maintainable server-side applications. Choose patterns that fit your complexity level.
