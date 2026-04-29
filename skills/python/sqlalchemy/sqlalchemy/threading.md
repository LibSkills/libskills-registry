# SQLAlchemy — Threading

## Sessions Are Not Thread-Safe

Each `Session` / `AsyncSession` instance must stay within a single thread or async task. Sharing a session across threads causes data corruption and deadlocks.

| Object | Thread-safe? | Notes |
|--------|-------------|-------|
| `Engine` / `AsyncEngine` | Yes | Connection pooling, thread-safe by design |
| `Session` / `AsyncSession` | **No** | One session per thread/async task |
| `sessionmaker` factory | Yes | Factory is safe; sessions it creates are not |
| ORM mapped instances | **No** | Mutating from multiple threads corrupts identity map |
| `Result` / `ScalarResult` | **No** | Must be consumed in the creating thread/task |

## Connection Pool Threading

The engine's connection pool (`QueuePool` by default) is thread-safe. Multiple threads can check out connections simultaneously.

```python
# Engine is global and shared — thread-safe
engine = create_engine("postgresql://user:pass@localhost/db")

def worker():
    # Each thread creates its own session
    with Session(engine) as session:
        result = session.execute(select(User))
        # ...
```

## Async Concurrency

With async drivers (asyncpg, aiosqlite), use `AsyncSession` per coroutine:

```python
# CORRECT: one AsyncSession per task
async def process_user(user_id: int):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()

# Call concurrently — each gets its own session
await asyncio.gather(*[process_user(i) for i in range(10)])
```

## Greenlet / Thread Safety in Sync Code

SQLAlchemy 2.0's "sync" API uses greenlets internally when called in async context via `run_sync()`. Each greenlet is single-threaded.

```python
# sync code inside async context
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # `run_sync` executes sync code in a greenlet
        # Still safe — greenlets don't parallelize
```

## Asyncio Task Affinity

An `AsyncSession` is bound to the async task (or event loop) that created it. Do not pass `AsyncSession` to a different loop.

```python
# WRONG: session created in one loop, used in another
loop1 = asyncio.new_event_loop()
session = AsyncSession(engine)  # bound to loop1

loop2 = asyncio.new_event_loop()
loop2.run_until_complete(session.execute(...))  # ❌ RuntimeError
```
