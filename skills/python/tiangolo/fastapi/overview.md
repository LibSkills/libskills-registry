# fastapi — Overview

**FastAPI** is a modern, high-performance Python web framework for building APIs with Python type hints. It auto-generates OpenAPI documentation, validates requests with Pydantic, and supports async endpoints via ASGI.

## When to Use

- REST API backends that need auto-generated docs (OpenAPI/Swagger)
- Services that benefit from type-based validation (Pydantic models)
- Async endpoints for I/O-bound workloads (database queries, HTTP calls)
- Microservices with clean separation of request/response models

## When NOT to Use

- Server-rendered HTML applications (use Jinja2 templates with FastAPI, or Django)
- WebSocket-heavy applications (FastAPI supports WS but is primarily REST-focused)
- CPU-bound endpoints (use a task queue like Celery offloaded from sync endpoints)
- Real-time bidirectional streaming (gRPC or raw WebSocket may be better)
- Simple scripts that don't need a web framework

## Key Design

- **Type-driven**: Python type hints define request/response schemas
- **Pydantic v2**: Data validation, serialization, and schema generation
- **ASGI**: Async Server Gateway Interface — runs on uvicorn/hypercorn
- **Dependency Injection**: `Depends()` for reusable logic (auth, DB sessions)
- **Automatic docs**: `/docs` (Swagger UI) and `/redoc` (ReDoc) endpoints
- **Path operations**: `@app.get()`, `@app.post()`, etc. with path/query/body params
