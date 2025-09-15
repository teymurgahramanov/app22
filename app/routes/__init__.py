# Routes package
from .app import router as app_router
from .system import router as system_router
from .http import router as http_router
from .filesystem import router as filesystem_router
from .database import router as database_router
from .todo import router as todo_router
from .mongodb import router as mongodb_router

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

# Main router that includes all sub-routers
router = APIRouter()

@router.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")

# Include all route modules
router.include_router(system_router)
router.include_router(app_router)
router.include_router(http_router)
router.include_router(filesystem_router)
router.include_router(database_router)
router.include_router(todo_router) 
router.include_router(mongodb_router)