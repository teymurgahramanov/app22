from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import app.database as database
import uuid
import datetime

# Pydantic models for request/response validation
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

def get_tasks(db: Session, limit: int = 10):
    tasks = db.query(database.Tasks).order_by(database.Tasks.updated_at.desc()).limit(limit).all()
    return tasks

def get_task(db: Session, task_id: str):
    task = db.query(database.Tasks).filter(database.Tasks.id == task_id).first()
    return task

def add_task(db: Session, task: TaskCreate):
    task_id = str(uuid.uuid4())
    db_task = database.Tasks(
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

def update_task(db: Session, task_id: str, task: TaskUpdate):
    db_task = get_task(db, task_id)
    if db_task is None:
        return None
    
    update_data = task.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(db_task)
    return db_task

def remove_task(db: Session, task_id: str):
    db_task = get_task(db, task_id)
    if db_task is None:
        return None
    
    db.delete(db_task)
    db.commit()
    return True