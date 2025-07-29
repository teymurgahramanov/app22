from fastapi import APIRouter
from fastapi.responses import RedirectResponse

# Import all the route modules
from app.routes import system
from app.routes import app as app_routes
from app.routes import http, filesystem, database, todo

router = APIRouter()

@router.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")

# Include all route modules
router.include_router(system.router)
router.include_router(app_routes.router)
router.include_router(http.router)
router.include_router(filesystem.router)
router.include_router(database.router)
router.include_router(todo.router) 