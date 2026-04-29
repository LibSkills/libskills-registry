# FastAPI — Quickstart

**When asked to write FastAPI code, use these patterns first.**

## 1. Hello World GET

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 2. CRUD + path/query parameters

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str

fake_db: list[Item] = []

@app.post("/items")
async def create_item(item: Item):
    fake_db.append(item)
    return item

@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):  # query params
    return fake_db[skip : skip + limit]

@app.get("/items/{item_id}")  # path param
async def get_item(item_id: int):
    for item in fake_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    for i, existing in enumerate(fake_db):
        if existing.id == item_id:
            fake_db[i] = item
            return item
    raise HTTPException(status_code=404)

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(fake_db):
        if item.id == item_id:
            fake_db.pop(i)
            return {"ok": True}
    raise HTTPException(status_code=404)
```

## 3. Pydantic model validation (request body)

```python
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    tags: list[str] = []

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
    tags: list[str]

@app.post("/items", response_model=ItemOut)
async def create_item(item: ItemCreate):
    # item is validated automatically; 422 on invalid input
    return ItemOut(id=1, **item.model_dump())
```

## 4. Dependency injection (Depends)

```python
from fastapi import Depends, FastAPI, Header, HTTPException

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    return authorization.removeprefix("Bearer ")

@app.get("/users/me")
async def get_current_user(token: str = Depends(verify_token)):
    return {"user_id": token}

# Dependencies can also be sync (run in threadpool)
def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
async def get_items(db=Depends(get_db)):
    return await db.query("SELECT * FROM items")
```

## 5. Database integration (async SQLAlchemy)

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3")
session_local = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

async def get_session():
    async with session_local() as session:
        yield session

@app.post("/users")
async def create_user(name: str, session: AsyncSession = Depends(get_session)):
    user = User(name=name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"id": user.id, "name": user.name}

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404)
    return {"id": user.id, "name": user.name}
```

## 6. File upload

```python
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename")
    contents = await file.read()
    # process contents or save to disk
    return {"filename": file.filename, "size": len(contents)}

# Multiple files
@app.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    return [{"filename": f.filename, "size": len(await f.read())} for f in files]
```

## 7. BackgroundTasks

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

@app.post("/send-notification")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"notification sent to {email}")
    return {"message": "Notification sent"}
```

## 8. WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        print("client disconnected")
```

## 9. Middleware

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(elapsed)
    return response
```

## Sync vs async endpoint rule

```python
# ✅ async def: for await-based operations
@app.get("/async-data")
async def get_data():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com")
    return r.json()

# ✅ def (sync): for CPU-bound or blocking operations (runs in threadpool)
@app.get("/sync-data")
def get_data():
    result = slow_db_query()  # blocks this thread, not the event loop
    return result
```
