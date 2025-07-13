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

@app.get("/tasks",response_model=List[TaskResponse])
def get_tasks(status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority level"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of tasks to return")):

    filtered_tasks = tasks_db
    if status:
            filtered_tasks = [task for task in filtered_tasks if task["status"] == status]
    
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task["priority"] == priority]
    
    # Apply pagination
    return filtered_tasks[skip:skip + limit]

@app.put("/tasks/{task_id}",response_model=TaskResponse)
def update_task(task_id:int,task_update:TaskUpdate):
    task=find_task(task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    
    update_data=task_update.dict(exclude_unset=True)
    for field,  value in update_data.items():
        task[field]=value
        task["updated_at"] = datetime.now()
    
    return task        

@app.delete("/tasks/{task_id}",response_model=TaskResponse)
def delete_task(task_id:int):
    task=find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    tasks_db.remove(task)
    
    return {"message": f"Task {task_id} deleted successfully"}

#get tasks summary

@app.get("tasks/stats/summary")
def get_task_stats():
    total_tasks=len(tasks_db)
    status_counts={
        "pending":0,
        "in_progress":0,
        "completed":0
    }

    priority_counts={i:0 for i in range (1,6)}

    for tasks in tasks_db:
        status_counts[tasks["status"]]+=1
        priority_counts[tasks["priority"]]+=1

    return{
        "total_tasks": total_tasks,
        "by_status": status_counts,
        "by_priority": priority_counts
    }


#mark task as completed 
@app.patch("tasks/{task_id}/complete")
def update_task_status(task_id:int):
    task=find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"]=TaskStatus.completed
    task["updated_at"]=datetime.now()

    return {"message":f"Task {task_id} marked as completed","task":task}


@app.get("/tasks/priority/{priority_level}",response_model=List[TaskResponse])
def get_tasks_by_priority(priority_level: int = Field(..., ge=1, le=5)):
    filtered_tasks = [task for task in tasks_db if task["priority"] == priority_level]
    return filtered_tasks

#clear all completed tasks 
@app.delete("/tasks/completed/clear")
def clear_completed_tasks():
    global tasks_db
    completed_count = len([tasks for tasks in tasks_db if tasks["status"] == TaskStatus.completed])
    tasks_db = [task for task in tasks_db if task["status"] != TaskStatus.completed]
    
    return {"message": f"Cleared {completed_count} completed tasks"}

    