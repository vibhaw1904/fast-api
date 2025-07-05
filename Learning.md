# FastAPI Learning Progress

## 1. Pydantic Models for Request and Response

**What are Pydantic Models?**
Pydantic models are Python classes that define the structure and validation rules for data. In FastAPI, they're used to:
- Define request body structure (what data comes in)
- Define response body structure (what data goes out)
- Automatically validate incoming data
- Generate API documentation

**How they work:**
- Create a class inheriting from `BaseModel`
- Define fields with type hints
- FastAPI automatically validates data against these models

**Simple Example:**

```python
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

# Request Model - defines what data we expect to receive
class UserCreate(BaseModel):
    name: str
    email: str
    age: int

# Response Model - defines what data we send back
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # FastAPI automatically validates incoming data against UserCreate model
    # If validation fails, it returns 422 error automatically
    
    # Simulate creating user with ID
    new_user = {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "age": user.age
    }
    
    # Return follows UserResponse model structure
    return new_user
```

**Key Benefits:**
- Automatic validation (age must be int, email must be string)
- Auto-generated API docs show expected request/response format
- Type safety and IDE support
- Automatic error responses for invalid data