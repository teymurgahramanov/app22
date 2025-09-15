import uuid
import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.routes.database import get_db, Tasks

# Pydantic models for request/response validation (moved from app/todo.py)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    done: Optional[bool] = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    done: bool
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# Todo business logic functions (moved from app/todo.py)
def get_tasks_logic(db: Session, limit: int = 10):
    tasks = db.query(Tasks).order_by(Tasks.updated_at.desc()).limit(limit).all()
    return tasks

def get_task_logic(db: Session, task_id: str):
    task = db.query(Tasks).filter(Tasks.id == task_id).first()
    return task

def add_task_logic(db: Session, task: TaskCreate):
    task_id = str(uuid.uuid4())
    db_task = Tasks(
        id=task_id,
        title=task.title,
        description=task.description,
        done=task.done,
        updated_at=datetime.datetime.now()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_logic(db: Session, task_id: str, task: TaskUpdate):
    db_task = get_task_logic(db, task_id)
    if db_task is None:
        return None
    
    update_data = task.model_dump(exclude_unset=True)  # Fixed deprecation warning
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(db_task)
    return db_task

def remove_task_logic(db: Session, task_id: str):
    db_task = get_task_logic(db, task_id)
    if db_task is None:
        return None
    
    db.delete(db_task)
    db.commit()
    return True

# Router for todo endpoints
router = APIRouter()

# Todo endpoints
@router.post("/tasks", response_model=TaskResponse, status_code=201, tags=["ToDo"])
def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Add new task."""
    return add_task_logic(db, task)

@router.get("/tasks", response_model=List[TaskResponse], tags=["ToDo"])
def get_tasks(
    limit: int = Query(10, description="Number of tasks to retrieve"),
    db: Session = Depends(get_db)
):
    """Get list of tasks."""
    return get_tasks_logic(db, limit)

@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["ToDo"])
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a specific task by ID."""
    task = get_task_logic(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse, tags=["ToDo"])
def update_task(task_id: str, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a specific task by ID."""
    updated_task = update_task_logic(db, task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/tasks/{task_id}", tags=["ToDo"])
def remove_task(task_id: str, db: Session = Depends(get_db)):
    """Remove a specific task by ID."""
    result = remove_task_logic(db, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"} 