# SQLAlchemy — Best Practices

## Session Per Request Pattern

Create one session per request/task and close it when done. Never share sessions.

```python
# FastAPI pattern
async def get_session():
    async with AsyncSession(engine) as session:
        yield session

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## Explicit Relationship Loading Strategy

Always specify loading strategy per query. The default `lazy="select"` causes N+1.

```python
# Per-query: use selectinload for to-many, joinedload for to-one
stmt = select(User).options(
    selectinload(User.posts),        # collection: 2nd query with IN clause
    joinedload(User.profile),        # to-one: JOIN in main query
)

# Model-level: set sensible defaults (avoids accidental N+1)
class User(Base):
    __tablename__ = "users"
    posts = relationship("Post", lazy="selectin")  # always eager via selectin
```

## Use `scalars()` for ORM Objects

`session.execute().scalars()` returns ORM objects directly. Without `scalars()`, you get tuples.

```python
# Returns [User, User, ...]
users = (await db.execute(select(User))).scalars().all()

# Returns [(User,), (User,), ...] — extra tuple wrapping
users = (await db.execute(select(User))).all()
```

## Bulk Operations With Core

Use Core-level insert/update/delete for bulk operations. ORM is for individual objects.

```python
# Bulk insert: 10x faster than ORM add()
await session.execute(
    insert(User),
    [{"name": f"user{i}", "email": f"user{i}@example.com"} for i in range(1000)]
)
await session.commit()

# Bulk update
await session.execute(
    update(User).where(User.is_active == True).values(updated_at=datetime.now(timezone.utc))
)
await session.commit()
```

## Use `with_loader_criteria()` for Global Filters

For soft-delete or multi-tenant apps, apply global filter without modifying every query.

```python
from sqlalchemy.orm import with_loader_criteria

stmt = select(Post).options(
    with_loader_criteria(Post, Post.deleted_at.is_(None), include_aliases=True)
)
```

## Type All Mapped Columns

v2.0 requires `Mapped[type]` annotations. This enables autocomplete, mypy, and pyright validation.

```python
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    age: Mapped[Optional[int]]  # nullable column
```
