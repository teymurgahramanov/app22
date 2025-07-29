import os
import hashlib
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Security: Define allowed file extensions
IGNORED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

@router.get("/cat", tags=["Filesystem"])
def cat() -> Dict[str, Any]:
    """Get contents and checksums of files mounted in the /app22/data directory.
    
    Returns:
        Dict containing file paths as keys and file info (checksum, content) as values.
        
    Raises:
        HTTPException: If data directory doesn't exist or is inaccessible.
    """
    data = {}
    data_path = Path("data")
    
    # Security: Ensure data directory exists and is accessible
    if not data_path.exists():
        logger.error(f"Data directory does not exist: {data_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data directory not found"
        )
    
    if not data_path.is_dir():
        logger.error(f"Data path is not a directory: {data_path}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data path is not a directory"
        )
    
    try:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                try:
                    filepath = Path(root) / file
                    absolute_filepath = filepath.resolve()
                    
                    # Security: Ensure the file is within the data directory
                    if not str(absolute_filepath).startswith(str(data_path.resolve())):
                        logger.warning(f"Attempted path traversal detected: {filepath}")
                        continue
                    
                    # Check file size for security
                    if absolute_filepath.stat().st_size > MAX_FILE_SIZE:
                        logger.warning(f"File too large, skipping: {absolute_filepath}")
                        data[str(absolute_filepath)] = {
                            'checksum': None,
                            'content': 'File too large to process',
                            'size': absolute_filepath.stat().st_size
                        }
                        continue
                    
                    # Get file extension
                    file_extension = absolute_filepath.suffix.lower()
                    
                    # Read file content
                    with open(absolute_filepath, 'rb') as f:
                        content = f.read()
                        checksum = hashlib.md5(content).hexdigest()
                        
                        data[str(absolute_filepath)] = {
                            'checksum': checksum,
                            'size': len(content)
                        }
                        
                        # Determine if content should be included
                        if file_extension in IGNORED_EXTENSIONS:
                            data[str(absolute_filepath)]['content'] = '-'
                            data[str(absolute_filepath)]['reason'] = 'Binary/image file excluded'
                        else:
                            try:
                                decoded_content = content.decode('utf-8')
                                data[str(absolute_filepath)]['content'] = decoded_content
                            except UnicodeDecodeError:
                                data[str(absolute_filepath)]['content'] = '-'
                                data[str(absolute_filepath)]['reason'] = 'Binary file - cannot decode as UTF-8'
                                
                except (OSError, IOError) as e:
                    logger.error(f"Error processing file {filepath}: {e}")
                    data[str(filepath)] = {
                        'checksum': None,
                        'content': f'Error reading file: {str(e)}',
                        'error': True
                    }
                except Exception as e:
                    logger.error(f"Unexpected error processing file {filepath}: {e}")
                    data[str(filepath)] = {
                        'checksum': None,
                        'content': 'Unexpected error processing file',
                        'error': True
                    }
                    
    except PermissionError:
        logger.error(f"Permission denied accessing data directory: {data_path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied accessing data directory"
        )
    except Exception as e:
        logger.error(f"Unexpected error walking data directory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing files"
        )
    
    logger.info(f"Successfully processed {len(data)} files from data directory")
    return data 