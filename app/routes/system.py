import os
import sys
import socket
import time
import datetime
import platform
import psutil
import logging
from fastapi import APIRouter

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
router = APIRouter()

@router.get("/sys", tags=["System"])
def info():
    """Get comprehensive system information."""
    data = {}
    
    # Basic system info
    data["hostname"] = socket.gethostname()
    data["timedate"] = datetime.datetime.now()
    data["uptime"] = time.time() - psutil.boot_time()
    
    # Platform information
    data["platform"] = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "platform": platform.platform()
    }
    
    # CPU information
    data["cpu"] = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "cpu_usage_percent": psutil.cpu_percent(interval=1)
    }
    
    # Memory information
    memory = psutil.virtual_memory()
    data["memory"] = {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free
    }
    
    return data

@router.get("/env", tags=["System"])
def env():
    """Get environment variables."""
    data = {}
    envVars = [(k,v) for k,v in os.environ.items()]
    for k,v in envVars:
        data[k] = v
    return data

@router.get("/crash", tags=["System"])
def crash():
    """Simulate a system crash."""
    os._exit(255) 