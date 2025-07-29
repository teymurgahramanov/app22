import time
from fastapi import APIRouter, Query, Request, Response

router = APIRouter()

@router.get("/headers", tags=["HTTP"])
def headers(request: Request):
    """Get request headers."""
    data = {}
    for k, v in request.headers.items():
        data[k] = v
    return data

@router.get("/response", tags=["HTTP"])
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