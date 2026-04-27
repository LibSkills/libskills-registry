# fastapi — Threading

## Async vs Sync Endpoints

| Endpoint Type | Runs On | Concurrency Model |
|---------------|---------|-------------------|
| `async def` | Event loop (main thread) | Cooperative multitasking |
| `def` | Threadpool (AnyIO) | Preemptive, one thread per request |

## When to Use async def

```python
# Use async def when endpoint does async I/O
@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com")  # non-blocking
        return r.json()
```

## When to Use def (sync)

```python
# Use def when endpoint does sync DB or CPU work
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()  # runs in threadpool
```

## Dependency Thread Safety

- Dependencies in `async def` endpoints run on the event loop (if async) or threadpool (if sync)
- Dependencies in `def` endpoints run in the threadpool
- Async dependencies with `yield` — cleanup runs on the same thread as setup

## Uvicorn Workers

```bash
# Single worker (development)
uvicorn main:app --reload

# Multiple workers (production)
uvicorn main:app --workers 4  # 4 processes, each with its own event loop
```

- Each worker is a separate OS process with its own event loop
- No shared memory between workers (use Redis/DB for shared state)
- Gunicorn + uvicorn workers for production process management

## Thread-Pool in async Endpoints

```python
import asyncio

@app.get("/mixed")
async def mixed():
    loop = asyncio.get_running_loop()
    # Offload sync work to threadpool
    result = await loop.run_in_executor(None, blocking_function)
    return {"result": result}
```
