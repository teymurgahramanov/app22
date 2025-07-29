from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi.responses import PlainTextResponse
from config import config
from app.routes.database import create_tables
from app.routes import router

# Define tags with descriptions for OpenAPI docs
tags_metadata = [
    {
        "name": "System",
        "description": "System information and monitoring endpoints. Get system stats, environment variables, and perform system operations.",
    },
    {
        "name": "ToDo", 
        "description": "Task management operations. Create, read, update, and delete tasks with full CRUD functionality.",
    },
    {
        "name": "HTTP",
        "description": "HTTP utilities and testing endpoints. Inspect headers, test responses, and debug HTTP requests.",
    },
    {
        "name": "Filesystem",
        "description": "File system operations and utilities. Read files, navigate directories, and perform file operations.",
    },
    {
        "name": "Database",
        "description": "Database connectivity and status monitoring. Check database health and connection status.",
    },
    {
        "name": "App",
        "description": "Application health, version information, and logging utilities. Monitor application status and retrieve logs.",
    },
]

def create_app():
    app = FastAPI(
        title="App22",
        description="The most useful web application to perform labs and tests in a container environment!",
        version=config.version or "1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=tags_metadata
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create database tables
    try:
        create_tables()
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    # Add Prometheus metrics endpoint
    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics():
        return generate_latest()
    
    # Include router
    app.include_router(router)
    
    return app 