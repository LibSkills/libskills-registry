# SQLAlchemy — Quickstart

**When asked to write Python database code, use these patterns first.**

## Async session with CRUD

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class UserRepo:
    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> User | None:
        return await db.get(User, user_id)

    @staticmethod
    async def list(db: AsyncSession) -> list[User]:
        result = await db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, name: str, email: str) -> User:
        user = User(name=name, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

# Usage
async def main():
    async with async_session() as db:
        user = await UserRepo.get(db, 1)
```

## N+1: Always use selectinload for relationships

```python
from sqlalchemy.orm import selectinload

# ✅ GOOD: eager load in one query
stmt = select(User).options(selectinload(User.posts)).limit(10)
result = await db.execute(stmt)
users = result.scalars().all()
for user in users:
    print(user.posts)  # no extra queries

# ❌ BAD: lazily loads posts per user — N+1
users = (await db.execute(select(User).limit(10))).scalars().all()
for user in users:
    print(user.posts)  # triggers one query per user
```

## Model definition

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

## Bulk insert

```python
db.add_all([User(name=f"user{i}") for i in range(100)])
await db.commit()
```
