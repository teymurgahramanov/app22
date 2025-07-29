import sys
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from config import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    stream=sys.stdout, 
    level=logging.INFO, 
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Response models
class VersionResponse(BaseModel):
    """Model for version response."""
    version: str

class HealthResponse(BaseModel):
    """Model for health check response."""
    healthy: bool
    timestamp: Optional[str] = None

class LogResponse(BaseModel):
    """Model for log response."""
    success: bool
    message: str
    logged_message: Optional[str] = None

# Global health status
healthy = True

@router.get("/version", response_model=VersionResponse, tags=["App"])
def version() -> VersionResponse:
    """Get application version.
    
    Returns:
        VersionResponse containing the current application version
    """
    try:
        app_version = config.version or "unknown"
        logger.debug(f"Version requested: {app_version}")
        return VersionResponse(version=app_version)
    except Exception as e:
        logger.error(f"Error retrieving version: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving application version"
        )

@router.get("/healthz/toggle", response_model=HealthResponse, tags=["App"])
def healthz_toggle() -> HealthResponse:
    """Toggle the health status.
    
    This endpoint allows you to simulate application health issues
    for testing purposes.
    
    Returns:
        HealthResponse with the new health status
    """
    global healthy
    try:
        old_status = healthy
        healthy = not healthy
        logger.info(f"Health status toggled from {old_status} to {healthy}")
        
        return HealthResponse(
            healthy=healthy,
            timestamp=str(config.version)
        )
    except Exception as e:
        logger.error(f"Error toggling health status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error toggling health status"
        )

@router.get("/healthz", response_model=HealthResponse, tags=["App"])
def healthz() -> HealthResponse:
    """Retrieve the health status.
    
    Returns:
        HealthResponse with current health status
        
    Raises:
        HTTPException: With 500 status if application is unhealthy
    """
    try:
        logger.debug(f"Health check requested, current status: {healthy}")
        
        if healthy:
            return HealthResponse(healthy=healthy)
        else:
            # Return 500 status when unhealthy
            logger.warning("Health check failed - application is unhealthy")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"healthy": healthy}
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error performing health check"
        )

@router.get("/log", response_model=LogResponse, tags=["App"])
def log(
    message: Optional[str] = Query(
        None, 
        description="Message to log at different log levels",
        max_length=1000  # Prevent extremely long log messages
    )
) -> LogResponse:
    """Log a message at different log levels.
    
    This endpoint logs the provided message at DEBUG, INFO, WARNING, and ERROR levels.
    Useful for testing log aggregation and monitoring systems.
    
    Args:
        message: The message to log (max 1000 characters)
        
    Returns:
        LogResponse confirming the logging operation
    """
    try:
        # Sanitize message for logging (prevent log injection)
        safe_message = message
        if message:
            # Replace newlines and carriage returns to prevent log injection
            safe_message = message.replace('\n', ' ').replace('\r', ' ')
            # Truncate if too long
            if len(safe_message) > 1000:
                safe_message = safe_message[:997] + "..."
        
        # Log at different levels
        logger.debug(safe_message)
        logger.info(safe_message)
        logger.warning(safe_message)
        logger.error(safe_message)
        
        return LogResponse(
            success=True,
            message="Message logged successfully at all levels",
            logged_message=safe_message
        )
        
    except Exception as e:
        logger.error(f"Error during logging operation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing log request"
        ) 