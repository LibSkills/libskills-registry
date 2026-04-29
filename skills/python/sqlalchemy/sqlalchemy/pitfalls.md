# SQLAlchemy — Pitfalls

Common mistakes that cause N+1 queries, stale data, or silently dropped writes.

## N+1 Query Problem

The most common SQLAlchemy performance trap. Accessing a related collection loads one query per parent row.

```python
# BAD: N+1 — one query for users, then N queries for posts
async def get_users_with_posts(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    for user in users:
        posts = await user.awaitable_attrs.posts  # ❌ one query per user!
        print(f"{user.name}: {len(posts)} posts")

# GOOD: eager load in one query
async def get_users_with_posts(db: AsyncSession):
    result = await db.execute(
        select(User).options(selectinload(User.posts))
    )
    users = result.scalars().all()
    for user in users:
        posts = user.posts  # ✅ already loaded — no extra query
        print(f"{user.name}: {len(posts)} posts")
```

## Stale ORM Objects After Commit

After `session.commit()`, objects are marked as "expired". Attribute access (except primary keys) triggers a DB reload. This can mask the actual state if the DB was modified by another transaction.

```python
# BAD: surprise reload after commit
session.add(user)
session.commit()  # user is now expired
print(user.name)  # ✅ triggers SELECT — but what if DB changed?

# GOOD: explicit refresh to get latest DB state
session.add(user)
session.commit()
session.refresh(user)  # ✅ explains the intent

# GOOD: use expire_on_commit=False to keep cached values
session = sessionmaker(engine, expire_on_commit=False)()
```

## Forgetting `await` on AsyncSession Operations

SQLAlchemy async API returns coroutines. Missing `await` means the coroutine is never executed — no query runs, no error.

```python
# BAD: silently does nothing
result = db.execute(select(User).where(User.id == 1))  # ❌ coroutine, not result
user = result.scalar_one_or_none()  # ❌ AttributeError: 'coroutine' has no attribute 'scalar_one_or_none'

# GOOD: await every async operation
result = await db.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()
```

## Session Leak / Context Manager Forgetting

Not closing a session leaks connections. In async code with asyncpg, this can exhaust the connection pool.

```python
# BAD: session never closed — connection pool leak
async def handler():
    db = AsyncSession(engine)
    result = await db.execute(select(User))
    # ❌ db.close() never called

# GOOD: context manager guarantees cleanup
async def handler():
    async with AsyncSession(engine) as db:
        result = await db.execute(select(User))

# ALSO GOOD: explicit close with try/finally
async def handler():
    db = AsyncSession(engine)
    try:
        result = await db.execute(select(User))
    finally:
        await db.close()
```

## Detached Object Access

After `session.close()` or `session.expunge()`, ORM objects become detached. Accessing unloaded attributes raises `DetachedInstanceError`.

```python
# BAD: accessing relation on detached object
async def get_user(db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == 1))
    user = result.scalar_one()
    await db.close()
    return user  # ❌ user is now detached

async def caller():
    user = await get_user()
    posts = await user.awaitable_attrs.posts  # DetachedInstanceError!

# GOOD: eager load what you need before closing
async def get_user(db: AsyncSession) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.posts)).where(User.id == 1)
    )
    user = result.scalar_one()
    await db.close()
    return user  # ✅ posts already loaded

async def caller():
    user = await get_user()
    posts = user.posts  # ✅ works because eager loaded
```

## Using `Model.query` (Old 1.x API) In 2.0

The `Model.query` property requires `sessionmaker` configured with `query_property` and is deprecated in 2.0.

```python
# BAD: old Query API (may not work with 2.0)
users = User.query.filter(User.name == "Alice").all()

# GOOD: new 2.0 select() API
stmt = select(User).where(User.name == "Alice")
result = session.execute(stmt)
users = result.scalars().all()
```

## Bulk Insert Performance with ORM

Using ORM objects for bulk inserts is dramatically slower than Core-level bulk inserts.

```python
# BAD: ORM per-row insert (slow, one-by-one)
for item in items:
    db.add(Item(name=item["name"], value=item["value"]))
await db.commit()  # N individual INSERTs

# GOOD: Core bulk insert via session
await db.execute(
    insert(Item), [{"name": item["name"], "value": item["value"]} for item in items]
)
await db.commit()  # single executemany
```
