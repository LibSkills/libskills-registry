# SQLAlchemy — Performance

## Throughput (approximate)

| Mode | Ops/sec | Notes |
|------|---------|-------|
| ORM fetch 1 row (by PK) | ~25K/s | Session + identity map overhead |
| Core fetch 1 row (by PK) | ~50K/s | No ORM mapping |
| ORM insert 1 row | ~5K/s | Flush + commit overhead |
| Core executemany (1000 rows) | ~100K rows/s | Single round trip |
| Async ORM (asyncpg) | ~30K/s | Async overhead lower than sync psycopg2 |

## Rules

- **Avoid ORM for bulk operations**: Use Core `insert()`/`update()` for >100 rows at once
- **Use selectinload over joinedload for collections**: selectinload issues a clean second query; joinedload may cartesian-product with other joins
- **Batch relationship loading**: When you need related data for multiple parents, use `selectinload()` — it issues `WHERE parent_id IN (...)` for the relationship
- **Control flush frequency**: Each `session.commit()` flushes all pending changes. Batch multiple operations before one commit
- **Index your FK columns**: SQLAlchemy does NOT auto-index foreign keys. Add `index=True` to every FK column

## Query Optimization

```python
# SLOW: loads all columns, then filters in Python
users = (await db.execute(select(User))).scalars().all()
active = [u for u in users if u.is_active]

# FAST: filter at the database
active = (await db.execute(
    select(User).where(User.is_active == True)
)).scalars().all()
```

## N+1 Detection

Enable echo and look for repeated identical queries:

```python
engine = create_async_engine(URL, echo=True)  # set to "debug" for full detail
```

Or use `set_session_options` with an event listener:

```python
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if "FROM users" in statement and statement.count("FROM users") > 3:
        log.warning(f"Potential N+1 detected: {statement}")
```

## Connection Pool Tuning

```python
engine = create_async_engine(
    URL,
    pool_size=10,          # persistent connections
    max_overflow=20,       # extra connections under load
    pool_pre_ping=True,    # test connection before use (recommended)
    pool_recycle=3600,     # recycle connections after 1 hour
)
```

## Lazy Loading Trade-offs

| Strategy | Query count | Memory | Best for |
|----------|-------------|--------|----------|
| `lazy="select"` (default) | 1+N | Low | Rarely-accessed relations |
| `lazy="selectin"` | 2 | Medium | To-many, most queries |
| `lazy="joinedload"` | 1 | High | To-one, always needed |
| `lazy="subquery"` | 2 | Medium | Complex to-many with filters |
| `lazy="raise"` | 1 (or error) | Low | Enforce explicit loading |

## Bulk INSERT Performance (async)

```python
# ORM: one-by-one — ~5K rows/sec
for user_data in users_data:
    session.add(User(**user_data))
await session.commit()

# Core executemany: ~200K rows/sec
from sqlalchemy import insert
await session.execute(
    insert(User), users_data
)
await session.commit()
```
