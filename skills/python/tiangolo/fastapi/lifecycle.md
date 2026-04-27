# fastapi — Lifecycle

## Application Startup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db_pool()
    yield
    # Shutdown
    await close_db_pool()

app = FastAPI(lifespan=lifespan)
```

## Lifespan Events (Deprecated)

```python
# DEPRECATED — use lifespan instead
@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()
```

## Dependency Lifecycle

- Dependencies with `yield` act as context managers
- Code before `yield` runs before the endpoint
- Code after `yield` runs after the response is sent

```python
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Request Lifecycle

```
Request → Middleware → Dependency Resolution → Endpoint → Response → Middleware
```

- Middleware wraps the entire request/response cycle
- Dependencies are resolved bottom-up (sub-dependencies first)
- Response model validation runs after the endpoint returns

## Background Tasks

```python
from fastapi import BackgroundTasks

@app.post("/send-email")
async def send_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_async, email="user@example.com")
    return {"message": "Email will be sent"}
# Background task runs AFTER the response is returned
```
