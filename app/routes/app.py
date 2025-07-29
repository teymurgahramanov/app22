import sys
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from config import config

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
router = APIRouter()

@router.get("/version", tags=["App"])
def version():
    """Get version."""
    return config.version

healthy = True

@router.get("/healthz/toggle", tags=["App"])
def healthz_toggle():
    """Toggle the health status."""
    global healthy
    healthy = not healthy
    return {"healthy": healthy}

@router.get("/healthz", tags=["App"])
def healthz():
    """Retrieve the health status."""
    if healthy:
        return {"healthy": healthy}
    else:
        raise HTTPException(status_code=500, detail={"healthy": healthy})

@router.get("/log", tags=["App"])
def log(message: Optional[str] = Query(None, description="Message to log")):
    """Log a message at different log levels."""
    logging.debug(message)
    logging.info(message)
    logging.warning(message)
    logging.error(message)
    return True 