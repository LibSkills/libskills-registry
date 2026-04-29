"""
SQLAlchemy 2.0 async example — FastAPI-style User/Post model with queries.

Run:
    pip install sqlalchemy asyncio aiosqlite
    python basic.py
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    posts: Mapped[list["Post"]] = relationship(back_populates="author", lazy="selectin")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str]
    author_id: Mapped[int] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    author: Mapped["User"] = relationship(back_populates="posts")


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        # Create
        alice = User(name="Alice", email="alice@example.com")
        session.add(alice)
        await session.commit()

        bob = User(name="Bob", email="bob@example.com")
        session.add(bob)
        await session.commit()

        post = Post(title="Hello World", body="First post!", author_id=alice.id)
        session.add(post)
        await session.commit()

        # Read with relationship (N+1 avoided via selectinload)
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.name}, Posts: {len(user.posts)}")
            for p in user.posts:
                print(f"  - {p.title}")

        # Update
        result = await session.execute(select(User).where(User.email == "alice@example.com"))
        found = result.scalar_one()
        found.name = "Alice Updated"
        await session.commit()

        # Delete
        result = await session.execute(select(User).where(User.email == "bob@example.com"))
        to_delete = result.scalar_one()
        await session.delete(to_delete)
        await session.commit()

        # Verify
        result = await session.execute(select(User))
        remaining = result.scalars().all()
        print(f"Remaining users: {[u.name for u in remaining]}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
