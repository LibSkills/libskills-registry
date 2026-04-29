# FastAPI — Quickstart

**When asked to write FastAPI code, use these patterns first.**

## File upload endpoint (the most common miss)

```python
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
import hashlib

app = FastAPI()

async def hash_file(file: UploadFile) -> str:
    sha256 = hashlib.sha256()
    while chunk := await file.read(8192):
        sha256.update(chunk)
    return sha256.hexdigest()

@app.post("/hash", status_code=status.HTTP_200_OK)
async def upload_hash(
    file: UploadFile = File(...),
    hasher: str = Depends(hash_file),     # ✅ callable dependency
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    return {"filename": file.filename, "sha256": hasher}
```

## Sync vs async endpoint rule

```python
# ✅ async def: for await-based operations (database via async ORM, httpx)
@app.get("/async-data")
async def get_data():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com")
    return r.json()

# ✅ def (sync): for CPU-bound or blocking operations
@app.get("/sync-data")
def get_data():  # FastAPI runs this in a threadpool automatically
    result = slow_db_query()  # blocks this thread, not the event loop
    return result
```

## CRUD with Pydantic models

```python
from pydantic import BaseModel

class ItemOut(BaseModel):
    id: int
    name: str

class ItemCreate(BaseModel):
    name: str

@app.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    item = await fetch_item(item_id)
    if not item:
        raise HTTPException(status_code=404)
    return item
```

## Dependency injection

```python
from fastapi import Depends, FastAPI

def get_db():  # sync is fine, runs in threadpool
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
async def get_users(db=Depends(get_db)):
    return await db.query("SELECT * FROM users")
```
