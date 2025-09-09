import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Query, Request, Response, HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/headers", tags=["HTTP"])
def headers(request: Request) -> Dict[str, str]:
    """Get request headers.
    
    Args:
        request: FastAPI request object containing headers
        
    Returns:
        Dictionary of all request headers (keys are lowercase)
    """
    try:
        data = {}
        for key, value in request.headers.items():
            data[key] = value
        
        logger.info(f"Retrieved {len(data)} headers")
        return data
        
    except Exception as e:
        logger.error(f"Error processing headers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing request headers"
        )

@router.get("/response", tags=["HTTP"])
def response(
    status_code: int = Query(
        200, 
        alias="status",
        description="HTTP status code to return",
        ge=100,  # HTTP status codes start at 100
        le=599   # HTTP status codes go up to 599
    ),
    delay: int = Query(
        0, 
        description="Delay in seconds before returning the response",
        ge=0,    # Delay cannot be negative
        le=300   # Maximum delay of 5 minutes for safety
    ),
    response: Response = None
) -> Dict[str, Any]:
    """Simulate HTTP response with optional status and delay.
    
    Args:
        status_code: HTTP status code to return (100-599)
        delay: Delay in seconds before returning response (0-300)
        response: FastAPI response object to modify
        
    Returns:
        Dictionary containing the status code and delay information
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        logger.info(f"Simulating response with status {status_code} and delay {delay}s")
        
        # Validate status code is a valid HTTP status
        if status_code < 100 or status_code > 599:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Status code must be between 100 and 599"
            )
        
        # Validate delay is reasonable
        if delay < 0 or delay > 300:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Delay must be between 0 and 300 seconds"
            )
        
        data = {
            'status': status_code,
            'delay': delay,
            'timestamp': time.time()
        }
        
        # Apply delay if specified
        if delay > 0:
            logger.debug(f"Applying delay of {delay} seconds")
            time.sleep(delay)
        
        # Set the response status code
        if response:
            response.status_code = status_code
        
        logger.info(f"Response simulation completed successfully")
        return data
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        logger.error(f"Unexpected error in response simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error simulating response"
        ) 