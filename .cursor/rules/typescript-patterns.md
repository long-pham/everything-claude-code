---
description: "TypeScript/JavaScript patterns: API response interface, React hooks, repository pattern"
globs: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
alwaysApply: false
---

# TypeScript/JavaScript Patterns

> This file extends [common/patterns.md](../common/patterns.md) with TypeScript/JavaScript specific content.

## API Response Format

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

## Dependency Injection Pattern

```python
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbSession = Annotated[Session, Depends(get_db)]

async def get_users(db: DbSession) -> list[User]:
    return db.query(User).all()
```

## Repository Pattern

```python
from typing import Protocol, TypeVar
from abc import abstractmethod

T = TypeVar("T")

class Repository(Protocol[T]):
    @abstractmethod
    async def find_all(self, filters: dict | None = None) -> list[T]: ...

    @abstractmethod
    async def find_by_id(self, id: str) -> T | None: ...

    @abstractmethod
    async def create(self, data: dict) -> T: ...

    @abstractmethod
    async def update(self, id: str, data: dict) -> T: ...

    @abstractmethod
    async def delete(self, id: str) -> None: ...
```

## Service Layer Pattern

```python
from dataclasses import dataclass

@dataclass
class UserService:
    repository: UserRepository

    async def create_user(self, data: UserCreate) -> User:
        # Business logic here
        existing = await self.repository.find_by_email(data.email)
        if existing:
            raise ValueError("Email already exists")
        return await self.repository.create(data.model_dump())
```

## Context Manager Pattern

```python
from contextlib import contextmanager, asynccontextmanager
from collections.abc import Generator, AsyncGenerator

@contextmanager
def managed_resource() -> Generator[Resource, None, None]:
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.cleanup()

@asynccontextmanager
async def async_managed_resource() -> AsyncGenerator[Resource, None]:
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await resource.cleanup()
```
