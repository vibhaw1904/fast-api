from typing import Union

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

app=FastAPI(
     title="My First FastAPI App",
    description="Learning FastAPI step by step",
    version="1.0.0"
);


# Enum for task status
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

# Pydantic models for request/response
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=500, description="Task description")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5)")
    status: TaskStatus = Field(TaskStatus.pending, description="Task status")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[TaskStatus] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

# In-memory storage (in real apps, you'd use a database)
tasks_db = []
next_id = 1


class Item(BaseModel):
    name:str
    price:float
    is_offer:Union[bool, None] = None

@app.get("/")
def read_root():
    return {"hello its vibhaw , my first api"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}




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



#helper function to find task
def find_task(task_id:int):
    for task in tasks_db:
        if(task["id"]==task_id):
            return task
        return None

@app.post("/create-task",response_model=TaskResponse, status_code=201)
def create_task(task:TaskCreate):
    global next_id
    now= datetime.now()
    new_task={
        "id":next_id,
        "title":task.title,
        "description":task.description,
        "priority":task.priority,
        "status":task.status,
        "created_at": now,
        "updated_at": now
    }
    tasks_db.append(new_task)
    next_id+=1
    return new_task