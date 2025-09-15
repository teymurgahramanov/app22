import os
import hashlib
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Security: Define allowed file extensions
IGNORED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

@router.get("/cat", tags=["Filesystem"])
def cat() -> Dict[str, Any]:
    """Compatibility endpoint that returns the contents and checksums of files under data/.

    The response is a mapping of absolute file path to an object containing
    checksum and content (or '-' for binary/ignored types), matching tests' expectations.
    """
    results: Dict[str, Any] = {}
    for root, dirs, files in os.walk("data"):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            try:
                with open(abs_path, 'rb') as f:
                    content = f.read()
                    checksum = hashlib.md5(content).hexdigest()
                    ext = Path(abs_path).suffix.lower()
                    if ext in IGNORED_EXTENSIONS:
                        results[abs_path] = {"checksum": checksum, "content": "-"}
                    else:
                        try:
                            decoded = content.decode('utf-8')
                            results[abs_path] = {"checksum": checksum, "content": decoded}
                        except UnicodeDecodeError:
                            results[abs_path] = {"checksum": checksum, "content": "-"}
            except FileNotFoundError:
                # Let this propagate so tests expecting this behavior pass
                raise
            except Exception as e:
                # For unexpected errors, surface minimal info
                results[abs_path] = {"checksum": None, "content": "-", "error": str(e)}
    return results

@router.get("/files", tags=["Filesystem"])
def files(file: Optional[str] = Query(None, description="Path to specific file to read"),
          ls: Optional[bool] = Query(None, description="List files in directory")) -> Dict[str, Any]:
    """Filesystem operations on the /app22/data directory.
    
    Args:
        file: Path to specific file to read (returns content and checksum)
        ls: If True, returns list of files with paths
        
    Returns:
        - Default (no params): Dict with count and total_size_bytes
        - file param: Dict with content, checksum, size for specific file
        - ls param: Dict with files list containing paths
        
    Raises:
        HTTPException: If data directory doesn't exist, file not found, or access denied.
    """
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
    
    # Handle specific file request
    if file is not None:
        return _get_file_content(data_path, file)
    
    # Handle list files request
    if ls is True:
        return _list_files(data_path)
    
    # Default: return count and total size
    return _get_directory_stats(data_path)


def _get_file_content(data_path: Path, file_path: str) -> Dict[str, Any]:
    """Get content and checksum of a specific file."""
    try:
        # Security: Resolve the file path and ensure it's within data directory
        requested_file = (data_path / file_path).resolve()
        
        # Security: Ensure the file is within the data directory
        if not str(requested_file).startswith(str(data_path.resolve())):
            logger.warning(f"Attempted path traversal detected: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: path traversal not allowed"
            )
        
        # Check if file exists
        if not requested_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}"
            )
        
        if not requested_file.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a file: {file_path}"
            )
        
        # Check file size for security
        file_size = requested_file.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {requested_file}")
            return {
                'path': file_path,
                'checksum': None,
                'content': 'File too large to process',
                'size': file_size,
                'error': 'File exceeds maximum size limit'
            }
        
        # Get file extension
        file_extension = requested_file.suffix.lower()
        
        # Read file content
        with open(requested_file, 'rb') as f:
            content = f.read()
            checksum = hashlib.md5(content).hexdigest()
            
            result = {
                'path': file_path,
                'checksum': checksum,
                'size': len(content)
            }
            
            # Determine if content should be included
            if file_extension in IGNORED_EXTENSIONS:
                result['content'] = '-'
                result['reason'] = 'Binary/image file excluded'
            else:
                try:
                    decoded_content = content.decode('utf-8')
                    result['content'] = decoded_content
                except UnicodeDecodeError:
                    result['content'] = '-'
                    result['reason'] = 'Binary file - cannot decode as UTF-8'
            
            return result
            
    except HTTPException:
        raise
    except (OSError, IOError) as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while reading file"
        )


def _list_files(data_path: Path) -> Dict[str, Any]:
    """Get list of files with their paths."""
    files_list: List[Dict[str, Any]] = []
    
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
                    
                    # Get relative path from data directory
                    relative_path = filepath.relative_to(data_path)
                    file_size = absolute_filepath.stat().st_size
                    
                    files_list.append({
                        'path': str(relative_path),
                        'absolute_path': str(absolute_filepath),
                        'size': file_size,
                        'extension': absolute_filepath.suffix.lower()
                    })
                    
                except (OSError, IOError) as e:
                    logger.error(f"Error accessing file {filepath}: {e}")
                    files_list.append({
                        'path': str(filepath.relative_to(data_path)) if filepath else file,
                        'error': f"Error accessing file: {str(e)}"
                    })
                except Exception as e:
                    logger.error(f"Unexpected error processing file {filepath}: {e}")
                    files_list.append({
                        'path': file,
                        'error': 'Unexpected error processing file'
                    })
        
        return {
            'files': files_list,
            'count': len(files_list)
        }
        
    except PermissionError:
        logger.error(f"Permission denied accessing data directory: {data_path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied accessing data directory"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while listing files"
        )


def _get_directory_stats(data_path: Path) -> Dict[str, Any]:
    """Get count and total size of files in data directory."""
    count = 0
    total_size = 0
    
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
                    
                    file_size = absolute_filepath.stat().st_size
                    count += 1
                    total_size += file_size
                    
                except (OSError, IOError) as e:
                    logger.error(f"Error accessing file {filepath}: {e}")
                    # Still count the file even if we can't get size
                    count += 1
                except Exception as e:
                    logger.error(f"Unexpected error processing file {filepath}: {e}")
                    count += 1
        
        logger.info(f"Directory stats: {count} files, {total_size} bytes total")
        return {
            'count': count,
            'total_size_bytes': total_size
        }
        
    except PermissionError:
        logger.error(f"Permission denied accessing data directory: {data_path}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied accessing data directory"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting directory stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while getting directory statistics"
        ) 