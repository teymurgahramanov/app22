import datetime
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, Request, status

from config import config

logger = logging.getLogger(__name__)

router = APIRouter()


class MongoRequestRecord(BaseModel):
    id: str = Field(..., description="MongoDB document ID")
    timestamp: datetime.datetime
    source: str


class MongoDatabaseStatusResponse(BaseModel):
    db: str
    connected: bool
    writable: bool
    data: List[MongoRequestRecord]
    exception: Optional[str] = None


def _get_mongo_client():
    try:
        # Lazy import to avoid hard dependency in environments without pymongo
        from pymongo import MongoClient  # type: ignore
    except Exception as import_error:  # pragma: no cover
        raise RuntimeError(
            f"pymongo is required for /mongodb endpoint but is not installed: {import_error}"
        )

    client = MongoClient(
        config.mongo_uri,
        serverSelectionTimeoutMS=config.mongo_server_selection_timeout_ms,
        **(config.mongo_client_options or {})
    )
    return client


@router.get("/mongodb", response_model=MongoDatabaseStatusResponse, tags=["Database"])
def mongodb_status(
    limit: int = Query(5, ge=0, le=1000),
    request: Request = None,
):
    response = {
        "db": config.mongo_uri,
        "connected": True,
        "writable": True,
        "data": [],
        "exception": None,
    }

    client = None
    try:
        client = _get_mongo_client()
        db = client.get_database(config.mongo_db)
        collection = db.get_collection(config.mongo_collection)

        # Write a heartbeat document
        client_ip = "unknown"
        if request and hasattr(request, "client") and request.client:
            client_ip = request.client.host or "unknown"

        try:
            insert_result = collection.insert_one(
                {
                    "timestamp": datetime.datetime.utcnow(),
                    "source": client_ip,
                }
            )
            inserted_id = str(insert_result.inserted_id)
        except Exception as write_error:
            logger.error(f"MongoDB write error: {write_error}")
            response["writable"] = False
            response["exception"] = f"Write error: {write_error}"

        try:
            if limit == 0:
                cursor = []
            else:
                cursor = collection.find({}, sort=[("_id", -1)])
                # Support both pymongo Cursor and plain iterables in tests
                if hasattr(cursor, "limit"):
                    cursor = cursor.limit(limit)
                else:
                    try:
                        cursor = list(cursor)[:limit]
                    except TypeError:
                        # Fallback: leave as-is if not sliceable
                        pass

            for doc in cursor:
                try:
                    response["data"].append(
                        MongoRequestRecord(
                            id=str(doc.get("_id")),
                            timestamp=doc.get("timestamp"),
                            source=doc.get("source", "unknown"),
                        )
                    )
                except Exception as serialize_error:
                    logger.warning(
                        f"Error serializing MongoDB document {doc.get('_id')}: {serialize_error}"
                    )
        except Exception as read_error:
            logger.error(f"MongoDB read error: {read_error}")
            response["connected"] = False
            if response["exception"]:
                response["exception"] += f"; Read error: {read_error}"
            else:
                response["exception"] = f"Read error: {read_error}"

        if not response["connected"] and not response["writable"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MongoDB is completely unavailable",
            )

        return MongoDatabaseStatusResponse(**response)
    except RuntimeError as e:
        # pymongo missing
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except HTTPException:
        # Propagate HTTPExceptions such as 503 without converting to 500
        raise
    except Exception as e:
        logger.error(f"Unexpected MongoDB error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error interacting with MongoDB",
        )
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:
            pass


