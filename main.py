from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI(
     title="My First FastAPI App",
    description="Learning FastAPI step by step",
    version="1.0.0"
);


class Item(BaseModel):
    name:str
    price:float
    is_offer:Union[bool, None] = None

@app.get("/")
def read_root():
    return {"hello its vibhaw , my first api"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}




@app.put("/items/{item_id}")
def update_item(item_id:int,item:Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/items/")
def create_item(item:Item):
    return {"item_name":item.name,"item_price":item.price,"item_is_offer":item.is_offer}


@app.delete("/items/{item_id}")
def delete_item(item_id:int):
    return {"item_id":item_id}


#route with query parameters

@app.get("/items/")
def read_item(skip:int=0,limit:int=10):
    """
    Get items with pagination
    - skip: Number of items to skip
    - limit: Maximum number of items to return
    """
    return {"skip":skip,"limit":limit,"items":[f"Item {i}" for i in range(skip, skip + limit)]} 

#multiple path and query parameters

@app.get("/users/{user_id}/items/{item_id}")
def read_user_ietm(user_id:int,item_id:int,q:Union[str,None]=None,short:bool=False):
    """
    Get specific item for a specific user
    """
    return {
        "user_id": user_id, 
        "item_id": item_id,
        "description": f"Item {item_id} belongs to User {user_id}"
    }