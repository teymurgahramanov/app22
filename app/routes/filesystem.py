import os
import hashlib
from fastapi import APIRouter

router = APIRouter()

@router.get("/cat", tags=["Filesystem"])
def cat():
    """Get contents and checksums of files mounted in the /app22/data."""
    data = {}
    for root, dirs, files in os.walk("data"):
        for file in files:
            filepath = os.path.abspath(os.path.join(root, file))
            ignored_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg'}
            _, ext = os.path.splitext(filepath)
            with open(filepath, 'rb') as f:
                content = f.read()
                checksum = hashlib.md5(content).hexdigest()
                data[filepath] = {}
                data[filepath]['checksum'] = checksum
                if ext.lower() in ignored_extensions:
                    data[filepath]['content'] = '-'
                    continue
                try:
                    data[filepath]['content'] = content.decode('utf-8')
                except:
                    data[filepath]['content'] = '-'
                    pass
    return data 