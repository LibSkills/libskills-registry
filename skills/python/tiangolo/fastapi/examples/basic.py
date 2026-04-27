from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Annotated

app = FastAPI(title="Example API", version="1.0.0")


class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    is_available: bool = True


class ItemOut(Item):
    id: int


# In-memory store for demo
items_db: dict[int, Item] = {}
next_id = 1


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/items", response_model=ItemOut, status_code=201)
async def create_item(item: Item):
    global next_id
    item_id = next_id
    next_id += 1
    items_db[item_id] = item
    return ItemOut(id=item_id, **item.model_dump())


@app.get("/items/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemOut(id=item_id, **items_db[item_id].model_dump())


@app.get("/items", response_model=list[ItemOut])
async def list_items():
    return [ItemOut(id=k, **v.model_dump()) for k, v in items_db.items()]
