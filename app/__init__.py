from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from app.routes.database import create_tables
from app.routes import router

# Define tags with descriptions for OpenAPI docs
tags_metadata = [
    {
        "name": "System",
        "description": "System information. Get system stats, environment variables, and simulate crash.",
    },
    {
        "name": "App",
        "description": "Application health, version information, and logging utilities. Test health probes, logging, monitoring, and various deployment strategies.",
    },
    {
        "name": "HTTP",
        "description": "HTTP utilities. Inspect headers, test responses, and debug HTTP requests.",
    },
    {
        "name": "Filesystem",
        "description": "File system operations. Read files, navigate directories, and perform file operations.",
    },
    {
        "name": "Database",
        "description": "Database connectivity and status testing.",
    },
    {
        "name": "ToDo", 
        "description": "ToDo app simulator. Create, read, update, and delete tasks.",
    }
]

def create_app():
    app = FastAPI(
        title="App22",
        description="The most useful web application to perform tests in the Kubernetes!",
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
    
    # Include router
    app.include_router(router)
    
    return app 