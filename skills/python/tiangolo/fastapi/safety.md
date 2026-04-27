# fastapi — Safety

Red lines — conditions that must NEVER occur.

## NEVER trust user input without Pydantic validation

FastAPI validates types, but NOT domain constraints. A `str` field may contain SQL injection, XSS payloads, or invalid data. Always add Pydantic validators for semantic checks.

```python
from pydantic import BaseModel, field_validator

class UserCreate(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("username must be alphanumeric")
        return v.strip().lower()
```

## NEVER use `async def` endpoints for synchronous external calls

Synchronous calls in `async def` endpoints block the event loop. This degrades to single-threaded performance — one slow request blocks all others.

```python
# NEVER: blocks all other async handlers
@app.get("/external")
async def call_external():
    return requests.get("https://slow-api.example.com", timeout=5).json()

# ALWAYS: use httpx with await
@app.get("/external")
async def call_external():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://slow-api.example.com", timeout=5)
        return r.json()
```

## NEVER expose raw ORM objects without response_model

SQLAlchemy lazy-loading triggers on attribute access during serialization. This can execute unbounded SQL queries, expose internal fields, or crash with detached instance errors.

## NEVER use `Optional` without explicit `None` default in Pydantic fields

```python
# BAD: field is required but type says Optional
class Item(BaseModel):
    description: Optional[str]  # required — confusing!

# GOOD: explicit
class Item(BaseModel):
    description: str | None = None  # optional, defaults to None
```

## NEVER disable CORS without understanding the risk

```python
# NEVER IN PRODUCTION
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)
# allow_credentials=True + allow_origins=["*"] is explicitly forbidden by browsers
# If somehow bypassed, any website can impersonate authenticated users

# GOOD: explicit origin list
app.add_middleware(CORSMiddleware, allow_origins=["https://myapp.com"], allow_credentials=True)
```
