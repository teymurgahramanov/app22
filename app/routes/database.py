import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import config

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

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Router for database endpoints
router = APIRouter()

@router.get("/database", tags=["Database"])
def add_request(
    limit: int = Query(5, description="Number of recent requests to retrieve"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """This endpoint inserts request and selects last N requests from the database along with the database status."""
    data = {'db': '', 'connected': True, 'writable': True, 'data': []}
    
    try:
        record = Requests(datetime.datetime.now(), request.client.host)
        db.add(record)
        db.commit()
    except Exception as e:
        print(e)
        data['writable'] = False
        data['exception'] = str(e)
        db.rollback()
        
    try:
        records = db.query(Requests).order_by(Requests.id.desc()).limit(limit).all()
        data['db'] = str(engine.url)
        for record in records:
            record_dict = {
                'id': record.id,
                'timestamp': record.timestamp,
                'source': record.source
            }
            data['data'].append(record_dict)
    except Exception as e:
        print(e)
        data['connected'] = False
        data['exception'] = str(e)
        
    return data 