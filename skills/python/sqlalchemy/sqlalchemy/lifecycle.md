# SQLAlchemy — Lifecycle

## Initialization

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# 1. Create the Engine (one per database)
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/dbname",
    pool_size=5,
    max_overflow=10,
    echo=False,     # set True to log SQL
)

# 2. Define Base
class Base(DeclarativeBase):
    pass

# 3. Create sessionmaker factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 4. Create tables (for development — use Alembic for production)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

## Session Lifecycle

Each Session represents a single transaction scope.

```python
# Option A: context manager (recommended)
async with AsyncSessionLocal() as session:
    async with session.begin():
        # all operations in one transaction
        session.add(User(name="Alice"))
        # session.begin() commits on success, rolls back on error

# Option B: explicit begin/commit
session = AsyncSessionLocal()
try:
    session.add(User(name="Bob"))
    await session.commit()
except Exception:
    await session.rollback()
    raise
finally:
    await session.close()
```

## Object States

| State | Description | In identity map? | In DB? |
|-------|-------------|-----------------|--------|
| Transient | Created with `User()`, not added to session | No | No |
| Pending | Added via `session.add()` | Yes | Not yet |
| Persistent | Flushed to DB but within active transaction | Yes | Yes (uncommitted) |
| Detached | Session closed or `session.expunge()` called | No | Depends |
| Deleted | `session.delete()` called | Until flush | Marked for delete |

## Migration Lifecycle

Production databases use Alembic, not `Base.metadata.create_all()`.

```bash
# Generate migration
alembic revision --autogenerate -m "add users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

```python
# alembic/env.py
from myapp.models import Base
target_metadata = Base.metadata
```

## Shutdown

```python
# Close all connections in the pool
await engine.dispose()

# Always call on application shutdown (FastAPI example)
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()
```
