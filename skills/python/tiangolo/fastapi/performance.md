# fastapi — Performance

## Throughput (approximate, modern x86_64)

| Config | Requests/sec | Notes |
|--------|-------------|-------|
| Single uvicorn worker (sync) | ~5K/s | SQLite DB, def endpoints |
| Single uvicorn worker (async) | ~15K/s | Async endpoints, httpx calls |
| 4 uvicorn workers (async) | ~50K/s | Multi-process, async |
| Gunicorn + 4 uvicorn workers | ~45K/s | Slight overhead from gunicorn |

## Performance Rules

- **async def > def** for I/O-bound endpoints (5-10x improvement under load)
- **def endpoints run in threadpool** — limited by threadpool size
- **Use connection pooling**: `httpx.AsyncClient` with `limits` for external API calls
- **Database pooling**: SQLAlchemy `pool_size=20, max_overflow=10`
- **Use `response_model`**: skips unnecessary serialization of internal ORM fields
- **Stream large responses**: `StreamingResponse` for files/multipart

## Response Optimization

```python
from fastapi.responses import ORJSONResponse

# orjson is 2-5x faster than stdlib json
app = FastAPI(default_response_class=ORJSONResponse)
```

## JSON Serialization

```python
# Pydantic v2 with rust backend: ~5x faster than v1 (pure Python)
class Model(BaseModel):
    model_config = {"from_attributes": True}  # enables ORM mode
```

## Background Tasks vs Celery

| Approach | Latency | When |
|----------|---------|------|
| `BackgroundTasks` | Immediate | Lightweight, fire-and-forget |
| Celery / RQ | Queue + worker startup | Heavy, long-running tasks |
