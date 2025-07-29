from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi.responses import PlainTextResponse
from config import config
from app.routes.database import create_tables
from app.routes import router

def create_app():
    app = FastAPI(
        title="App22",
        description="The most useful web application to perform labs and tests in a container environment!",
        version=config.version or "1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
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