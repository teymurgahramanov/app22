import os
import sys
import socket
import time
import glob
import datetime
import hashlib
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import app.todo as todo
import app.database as database
from config import config

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
router = APIRouter()

@router.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")

@router.get("/version", tags=["System"])
def version():
    """Get version."""
    return config.version

@router.get("/sys", tags=["System"])
def info():
    """Get system information."""
    data = {}
    data["hostname"] = socket.gethostname()
    data["timedate"] = datetime.datetime.now()
    return data

@router.get("/env", tags=["System"])
def env():
    """Get environment variables."""
    data = {}
    envVars = [(k,v) for k,v in os.environ.items()]
    for k,v in envVars:
        data[k] = v
    return data

@router.get("/crash", tags=["System"])
def crash():
    """Simulate a system crash."""
    os._exit(255)

healthy = True

@router.get("/healthz/toggle", tags=["System"])
def healthz_toggle():
    """Toggle the health status."""
    global healthy
    healthy = not healthy
    return {"healthy": healthy}

@router.get("/healthz", tags=["System"])
def healthz():
    """Retrieve the health status."""
    if healthy:
        return {"healthy": healthy}
    else:
        raise HTTPException(status_code=500, detail={"healthy": healthy})

@router.get("/log", tags=["System"])
def log(message: Optional[str] = Query(None, description="Message to log")):
    """Log a message at different log levels."""
    logging.debug(message)
    logging.info(message)
    logging.warning(message)
    logging.error(message)
    return True

@router.get("/headers", tags=["System"])
def headers(request: Request):
    """Get request headers."""
    data = {}
    for k, v in request.headers.items():
        data[k] = v
    return data

@router.get("/response", tags=["System"])
def response(
    status: int = Query(200, description="HTTP status code to return"),
    delay: int = Query(0, description="Delay in seconds before returning the response"),
    response: Response = None
):
    """Simulate HTTP response with optional status and delay."""
    data = {}
    data['status'] = status
    data['delay'] = delay
    time.sleep(delay)
    response.status_code = status
    return data

@router.get("/cat", tags=["System"])
def cat():
    """Get contents and checksums of files mounted in the /app22/data."""
    data = {}
    for root, dirs, files in os.walk("data"):
        for file in files:
            filepath = os.path.abspath(os.path.join(root, file))
            ignored_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg'}
            _, ext = os.path.splitext(filepath)
            with open(filepath, 'rb') as f:
                content = f.read()
                checksum = hashlib.md5(content).hexdigest()
                data[filepath] = {}
                data[filepath]['checksum'] = checksum
                if ext.lower() in ignored_extensions:
                    data[filepath]['content'] = '-'
                    continue
                try:
                    data[filepath]['content'] = content.decode('utf-8')
                except:
                    data[filepath]['content'] = '-'
                    pass
    return data

@router.get("/database", tags=["System"])
def add_request(
    limit: int = Query(5, description="Number of recent requests to retrieve"),
    request: Request = None,
    db: Session = Depends(database.get_db)
):
    """This endpoint inserts request and selects last N requests from the database along with the database status."""
    data = {'db': '', 'connected': True, 'writable': True, 'data': []}
    
    try:
        record = database.Requests(datetime.datetime.now(), request.client.host)
        db.add(record)
        db.commit()
    except Exception as e:
        print(e)
        data['writable'] = False
        data['exception'] = str(e)
        db.rollback()
        
    try:
        records = db.query(database.Requests).order_by(database.Requests.id.desc()).limit(limit).all()
        data['db'] = str(database.engine.url)
        for record in records:
            record_dict = {
                'id': record.id,
                'timestamp': record.timestamp,
                'source': record.source
            }
            data['data'].append(record_dict)
    except Exception as e:
        print(e)
        data['connected'] = False
        data['exception'] = str(e)
        
    return data

# Todo endpoints
@router.post("/tasks", response_model=todo.TaskResponse, status_code=201, tags=["ToDo"])
def add_task(task: todo.TaskCreate, db: Session = Depends(database.get_db)):
    """Add new task."""
    return todo.add_task(db, task)

@router.get("/tasks", response_model=List[todo.TaskResponse], tags=["ToDo"])
def get_tasks(
    limit: int = Query(10, description="Number of tasks to retrieve"),
    db: Session = Depends(database.get_db)
):
    """Get list of tasks."""
    return todo.get_tasks(db, limit)

@router.get("/tasks/{task_id}", response_model=todo.TaskResponse, tags=["ToDo"])
def get_task(task_id: str, db: Session = Depends(database.get_db)):
    """Get a specific task by ID."""
    task = todo.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=todo.TaskResponse, tags=["ToDo"])
def update_task(task_id: str, task: todo.TaskUpdate, db: Session = Depends(database.get_db)):
    """Update a specific task by ID."""
    updated_task = todo.update_task(db, task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/tasks/{task_id}", tags=["ToDo"])
def remove_task(task_id: str, db: Session = Depends(database.get_db)):
    """Remove a specific task by ID."""
    result = todo.remove_task(db, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
