# fastapi — Pitfalls

## Do NOT define sync endpoints that block the event loop

`def` (synchronous) endpoints run in a threadpool. But if you call blocking code inside an `async def` endpoint (database query without `await`, file I/O), you block the event loop.

```python
# BAD: blocks the event loop
@app.get("/data")
async def get_data():
    result = slow_sync_db_query()  # NO await — blocks all concurrent requests
    return {"data": result}

# GOOD: use run_in_executor or a sync endpoint
@app.get("/data")
def get_data():
    result = slow_sync_db_query()  # runs in threadpool automatically
    return {"data": result}
```

## Do NOT mix Pydantic v1 and v2 imports

FastAPI v0.100+ requires Pydantic v2. `from pydantic import BaseSettings` (v1) is removed. Use `pydantic_settings.BaseSettings` for settings.

```python
# BAD: ImportError on FastAPI >= 0.100
from pydantic import BaseSettings

# GOOD
from pydantic_settings import BaseSettings
```

## Do NOT forget `response_model` on endpoints that return ORM objects

Without `response_model`, FastAPI serializes the raw return value. SQLAlchemy ORM objects contain lazy-loading proxies that fail serialization.

```python
# BAD: 500 error when lazy-loaded relationship triggers
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()  # ORM objects — serialization fails

# GOOD: use response_model
@app.get("/users", response_model=list[UserOut])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

## Do NOT use mutable default values in dependency functions

```python
# BAD: list is shared across all invocations
def common_parameters(q: list[str] = []):
    return {"q": q}

# GOOD
def common_parameters(q: list[str] | None = None):
    if q is None:
        q = []
    return {"q": q}
```

## Do NOT define dependencies with the same parameter name

If two dependencies declare the same parameter name, FastAPI can't resolve the conflict. Use `Depends()` aliasing.

## Do NOT put CPU-bound work in async endpoints

```python
# BAD: blocks event loop
@app.get("/compute")
async def compute():
    return sum(i * i for i in range(10_000_000))

# GOOD: sync endpoint runs in threadpool
@app.get("/compute")
def compute():
    return sum(i * i for i in range(10_000_000))
```
