import datetime
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from config import config

# Configure logging
logger = logging.getLogger(__name__)

# Database setup (moved from app/database.py)
# Create engine
engine = create_engine(
    config.database_uri,
    echo=config.database_echo,
    **config.database_options
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Requests(Base):
    __tablename__ = "Requests"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime) 
    source = Column(String(15))

    def __init__(self, timestamp, source):
        self.timestamp = timestamp
        self.source = source

class Tasks(Base):
    __tablename__ = "Tasks"
    id = Column(String, primary_key=True)
    title = Column(String(48))
    description = Column(String(254))
    done = Column(Boolean, default=False)
    updated_at = Column(DateTime) 

    def __init__(self, id, title, description, done, updated_at):
        self.id = id
        self.title = title
        self.description = description
        self.done = done
        self.updated_at = updated_at

# Pydantic response models
class RequestRecord(BaseModel):
    """Model for individual request record."""
    id: int
    timestamp: datetime.datetime
    source: str
    
    class Config:
        from_attributes = True

class DatabaseStatusResponse(BaseModel):
    """Model for database status response."""
    db: str = Field(..., description="Database connection string")
    connected: bool = Field(..., description="Whether database connection is working")
    writable: bool = Field(..., description="Whether database writes are working")
    data: List[RequestRecord] = Field(..., description="Recent request records")
    exception: Optional[str] = Field(None, description="Error message if any operation failed")

# Create all tables
def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Router for database endpoints
router = APIRouter()

@router.get("/database", response_model=DatabaseStatusResponse, tags=["Database"])
def add_request(
    limit: int = Query(
        5, 
        description="Number of recent requests to retrieve",
        ge=0,
        le=1000  # Increased limit to 1000 for large queries
    ),
    request: Request = None,
    db: Session = Depends(get_db)
) -> DatabaseStatusResponse:
    """Insert current request and retrieve last N requests from the database along with database status.
    
    Args:
        limit: Number of recent requests to retrieve (0-1000)
        request: FastAPI request object for client info
        db: Database session dependency
        
    Returns:
        DatabaseStatusResponse with connection status and recent requests
        
    Raises:
        HTTPException: If there are critical database errors
    """
    response_data = {
        'db': '',
        'connected': True,
        'writable': True,
        'data': [],
        'exception': None
    }
    
    # Get client IP address safely
    client_ip = "unknown"
    if request and hasattr(request, 'client') and request.client:
        client_ip = request.client.host or "unknown"
    
    # Try to insert a new request record
    try:
        logger.debug(f"Inserting request record for client: {client_ip}")
        record = Requests(datetime.datetime.now(), client_ip)
        db.add(record)
        db.commit()
        logger.debug("Request record inserted successfully")
    except SQLAlchemyError as e:
        logger.error(f"Database write error: {e}")
        response_data['writable'] = False
        response_data['exception'] = f"Write error: {str(e)}"
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")
    except Exception as e:
        logger.error(f"Unexpected error during database write: {e}")
        response_data['writable'] = False
        response_data['exception'] = f"Unexpected write error: {str(e)}"
        try:
            db.rollback()
        except Exception:
            pass
    
    # Try to read recent requests
    try:
        logger.debug(f"Retrieving last {limit} request records")
        records = db.query(Requests).order_by(Requests.id.desc()).limit(limit).all()
        response_data['db'] = str(engine.url)
        
        # Convert records to response format
        for record in records:
            try:
                record_dict = RequestRecord(
                    id=record.id,
                    timestamp=record.timestamp,
                    source=record.source
                )
                response_data['data'].append(record_dict.model_dump())  # Fixed deprecation warning
            except Exception as e:
                logger.warning(f"Error serializing record {record.id}: {e}")
                continue
                
        logger.info(f"Successfully retrieved {len(response_data['data'])} request records")
        
    except SQLAlchemyError as e:
        logger.error(f"Database read error: {e}")
        response_data['connected'] = False
        if response_data['exception']:
            response_data['exception'] += f"; Read error: {str(e)}"
        else:
            response_data['exception'] = f"Read error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error during database read: {e}")
        response_data['connected'] = False
        if response_data['exception']:
            response_data['exception'] += f"; Unexpected read error: {str(e)}"
        else:
            response_data['exception'] = f"Unexpected read error: {str(e)}"
    
    # If both operations failed, this might be a critical error
    if not response_data['connected'] and not response_data['writable']:
        logger.critical("Both database read and write operations failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is completely unavailable"
        )
    
    return DatabaseStatusResponse(**response_data) 