# fastapi — Best Practices

## Use Pydantic models for all request/response data

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    age: int = Field(ge=0, le=150)

class UserOut(BaseModel):
    id: int
    username: str
    email: str

@app.post("/users", response_model=UserOut)
async def create_user(user: UserCreate):
    return await save_user(user)
```

## Structure dependencies for clean code

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user = verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401)
    return user

@app.get("/me")
async def me(user: User = Depends(get_current_user)):
    return user
```

## Use APIRouter for modular applications

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users(): ...

@router.post("/")
async def create_user(): ...

app.include_router(router)
```

## Return correct status codes

```python
from fastapi import status

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return await save_user(user)

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    await remove_user(user_id)
    return  # no body for 204
```

## Handle errors with HTTPException

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## Enable CORS for browser-based APIs

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
